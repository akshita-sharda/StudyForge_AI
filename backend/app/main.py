import shutil
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from .core.config import settings
from .core.security import hash_password, verify_password, create_access_token
from .db import Base, engine, get_db
from .models import User, Document, Chunk, QuizAttempt, StudyTask
from .schemas import *
from .services import extract_and_chunk, retrieve, demo_questions, gemini_questions, gemini_chat, coach_answer

Base.metadata.create_all(bind=engine)
app = FastAPI(title="StudyForge AI API")
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_url, "http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:3002"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
oauth2 = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")
UPLOADS = Path("uploads"); UPLOADS.mkdir(exist_ok=True)
def current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)):
    try: user_id = int(jwt.decode(token, settings.secret_key, algorithms=["HS256"])["sub"])
    except (JWTError, ValueError): raise HTTPException(401, "Invalid session")
    user = db.get(User, user_id)
    if not user: raise HTTPException(401, "User not found")
    return user
@app.get("/health")
def health(): return {"status":"ok", "mock_ai":settings.mock_ai and not bool(settings.gemini_api_key), "gemini_enabled":bool(settings.gemini_api_key)}
@app.post("/api/v1/auth/signup", response_model=Token)
def signup(data: Signup, db:Session=Depends(get_db)):
    if db.query(User).filter_by(email=data.email).first(): raise HTTPException(400,"Email already registered")
    user=User(email=data.email, name=data.name, password_hash=hash_password(data.password)); db.add(user); db.commit(); db.refresh(user)
    return {"access_token":create_access_token(str(user.id))}
@app.post("/api/v1/auth/login", response_model=Token)
def login(data:Login, db:Session=Depends(get_db)):
    user=db.query(User).filter_by(email=data.email).first()
    if not user or not verify_password(data.password,user.password_hash): raise HTTPException(401,"Incorrect email or password")
    return {"access_token":create_access_token(str(user.id))}
@app.get("/api/v1/auth/me",response_model=UserOut)
def me(user:User=Depends(current_user)): return user
@app.put("/api/v1/onboarding")
def onboarding(data:Onboarding,user:User=Depends(current_user),db:Session=Depends(get_db)):
    user.goals=data.goals; user.learning_style=data.learning_style; db.commit(); return {"ok":True}
@app.get("/api/v1/documents")
def documents(user:User=Depends(current_user),db:Session=Depends(get_db)): return db.query(Document).filter_by(user_id=user.id).order_by(Document.created_at.desc()).all()
@app.post("/api/v1/documents")
def upload(title:str=Form(...),subject:str=Form(...),file:UploadFile=File(...),user:User=Depends(current_user),db:Session=Depends(get_db)):
    if file.content_type != "application/pdf": raise HTTPException(400,"Only PDFs are supported")
    doc=Document(user_id=user.id,title=title,subject=subject,filename=file.filename); db.add(doc); db.commit(); db.refresh(doc)
    path=UPLOADS/f"{doc.id}.pdf"
    with path.open("wb") as out: shutil.copyfileobj(file.file,out)
    try: extract_and_chunk(doc,path,db)
    except Exception: doc.status="failed"; db.commit(); raise HTTPException(422,"Could not process PDF")
    return doc
@app.delete("/api/v1/documents/{document_id}")
def delete_document(document_id:int,user:User=Depends(current_user),db:Session=Depends(get_db)):
    doc=db.get(Document,document_id)
    if not doc or doc.user_id!=user.id: raise HTTPException(404,"Document not found")
    db.delete(doc); db.commit(); return {"ok":True}
@app.post("/api/v1/chat")
def chat(data:ChatRequest,user:User=Depends(current_user),db:Session=Depends(get_db)):
    doc=db.get(Document,data.document_id)
    if not doc or doc.user_id!=user.id: raise HTTPException(404,"Document not found")
    retrieval_query = data.question
    if any(word in data.question.lower() for word in ("summary", "summarize", "summarise", "bullet", "revise", "revision", "quiz", "trick", "remember", "memorize", "memorise")):
        retrieval_query += " key concepts definitions explanations examples conclusions"
    planning_request = any(phrase in data.question.lower() for phrase in ("pick a chapter", "pick one chapter", "choose a chapter", "which chapter", "what should i study", "what do i study", "study next"))
    chunks = retrieve(db, doc.id, retrieval_query)
    # Planning needs the document's chapter map, not only the five chunks that
    # match the word "chapter" most often.
    if planning_request:
        chunks = db.query(Chunk).filter_by(document_id=doc.id).order_by(Chunk.page.asc()).limit(24).all()
    if not chunks or not chunks[0].content: return {"answer":"I don’t have enough evidence in this source yet. Try asking about a specific heading or upload a clearer PDF.","sources":[],"mode":"coach"}
    if settings.gemini_api_key:
        try:
            answer = gemini_chat(chunks, data.question, [item.model_dump() for item in data.history], settings.gemini_api_key, settings.gemini_model)
            return {"answer":answer,"sources":[{"page":c.page,"excerpt":c.content[:220]} for c in chunks],"mode":"gemini"}
        except RuntimeError as exc:
            raise HTTPException(502, str(exc)) from exc
    answer=coach_answer(chunks, data.question)
    return {"answer":answer,"sources":[{"page":c.page,"excerpt":c.content[:220]} for c in chunks],"mode":"coach"}
@app.post("/api/v1/quizzes/generate")
def generate_quiz(data:QuizRequest,user:User=Depends(current_user),db:Session=Depends(get_db)):
    doc=db.get(Document,data.document_id)
    if not doc or doc.user_id!=user.id: raise HTTPException(404,"Document not found")
    chunks = retrieve(db, doc.id, "key concepts important definitions examples applications")
    if not chunks: raise HTTPException(422, "This document has no extracted study text yet")
    if settings.gemini_api_key:
        try:
            questions = gemini_questions(chunks, data.count, settings.gemini_api_key, settings.gemini_model)
            return {"questions": questions, "mode": "gemini"}
        except RuntimeError as exc:
            raise HTTPException(502, str(exc)) from exc
    return {"questions":demo_questions(chunks,data.count),"mode":"demo"}
@app.post("/api/v1/quizzes/submit")
def submit_quiz(data:QuizSubmit,user:User=Depends(current_user),db:Session=Depends(get_db)):
    score=sum(a.correct_index==q.get("correct_index") for a,q in zip(data.answers,data.questions)); total=len(data.questions)
    db.add(QuizAttempt(user_id=user.id,document_id=data.document_id,score=score,total=total)); user.xp += score*10+10; db.commit()
    return {"score":score,"total":total,"xp_earned":score*10+10}
@app.get("/api/v1/progress")
def progress(user:User=Depends(current_user),db:Session=Depends(get_db)):
    attempts=db.query(QuizAttempt).filter_by(user_id=user.id).order_by(QuizAttempt.created_at.desc()).limit(5).all()
    return {"xp":user.xp,"streak":user.streak,"badges":["First Spark"] if user.xp else [],"recent_scores":[{"score":a.score,"total":a.total} for a in attempts]}
@app.post("/api/v1/study-plan")
def plan(data:PlanRequest,user:User=Depends(current_user),db:Session=Depends(get_db)):
    level = data.education_level.lower()
    if "10" in level:
        actions = ["make a colourful concept map from your textbook", "write 10 key definitions from memory", "solve 5 board-style questions step by step", "teach one difficult idea using a real-life example", "take a 10-minute recall quiz and correct every mistake"]
    elif "11" in level or "12" in level:
        actions = ["connect the chapter’s 5 core concepts in a one-page map", "derive or explain 3 important results without notes", "solve 5 exam-style application questions", "teach the hardest concept aloud in 3 minutes", "take a timed mini-test and analyse your weak spots"]
    else:
        actions = ["define the key theory and connect it to one real example", "compare two important ideas and explain the trade-off", "solve 5 discipline-level problems and log mistakes", "critique one claim or method from your notes", "take a retrieval check and write your next improvement target"]
    missions = [f"{data.education_level} · {data.subject}: {action}" for action in actions]
    tasks=[]
    for mission in missions:
        task=StudyTask(user_id=user.id,title=mission,due_date=data.exam_date,minutes=data.minutes_per_day); db.add(task); tasks.append(task)
    db.commit(); return tasks
@app.get("/api/v1/study-plan")
def get_plan(user:User=Depends(current_user),db:Session=Depends(get_db)): return db.query(StudyTask).filter_by(user_id=user.id).all()
@app.patch("/api/v1/study-plan/{task_id}")
def complete_task(task_id:int,user:User=Depends(current_user),db:Session=Depends(get_db)):
    task=db.get(StudyTask,task_id)
    if not task or task.user_id!=user.id: raise HTTPException(404,"Task not found")
    if not task.completed: task.completed=True; user.xp+=15
    db.commit(); return task
