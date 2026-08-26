import re
import json
from urllib import error as urlerror
from urllib import request as urlrequest
from pathlib import Path
import fitz
from sqlalchemy.orm import Session
from .models import Chunk, Document

def extract_and_chunk(document: Document, file_path: Path, db: Session):
    pdf = fitz.open(file_path)
    for page_number, page in enumerate(pdf, 1):
        text = page.get_text("text").strip()
        for part in re.findall(r'.{1,1000}(?:\s+|$)', text):
            if part.strip(): db.add(Chunk(document_id=document.id, page=page_number, content=part.strip()))
    document.status = "ready"; db.commit()

def retrieve(db: Session, document_id: int, question: str):
    stopwords = {"the", "a", "an", "is", "are", "to", "of", "in", "on", "for", "and", "or", "this", "that", "me", "my", "it", "all", "what", "how", "why", "can", "you"}
    terms = {term for term in re.findall(r"[a-zA-Z0-9]+", question.lower()) if len(term) > 2 and term not in stopwords}
    chunks = db.query(Chunk).filter_by(document_id=document_id).all()
    ranked = []
    for chunk in chunks:
        words = re.findall(r"[a-zA-Z0-9]+", chunk.content.lower())
        word_set = set(words)
        overlap = len(terms & word_set)
        phrase_bonus = 2 if question.lower().strip() in chunk.content.lower() else 0
        density = overlap / max(len(word_set), 1)
        ranked.append((overlap * 4 + phrase_bonus + density, chunk))
    ranked.sort(key=lambda item: item[0], reverse=True)
    selected = []
    seen = set()
    for score, chunk in ranked:
        normalized = re.sub(r"\s+", " ", chunk.content.lower()).strip()
        if normalized in seen:
            continue
        seen.add(normalized)
        selected.append(chunk)
        if len(selected) == 5:
            break
    return selected

def demo_questions(chunks, count):
    if not chunks:
        return []

    # Demo mode still needs to feel like a real recall exercise. Build each
    # question from a different retrieved passage instead of cloning one card.
    snippets = [re.sub(r"\s+", " ", chunk.content).strip()[:180] for chunk in chunks]
    snippets = [snippet for snippet in snippets if len(snippet) > 20]
    if not snippets:
        return []

    distractors = [
        "This idea is not mentioned anywhere in the source.",
        "The notes present the opposite conclusion.",
        "The source gives no information about this topic.",
    ]
    prompts = [
        "Which statement is best supported by your source?",
        "Which idea should you carry forward from this section?",
        "What does the evidence in your notes actually say?",
        "Choose the claim that belongs to this study world.",
        "Which recall signal matches the uploaded material?",
    ]

    questions = []
    for index in range(count):
        correct = snippets[index % len(snippets)]
        options = [correct, distractors[index % len(distractors)], distractors[(index + 1) % len(distractors)], distractors[(index + 2) % len(distractors)]]
        # Rotate the correct answer so every question does not reward the same click.
        correct_index = index % 4
        options[0], options[correct_index] = options[correct_index], options[0]
        questions.append({
            "question": prompts[index % len(prompts)],
            "options": options,
            "correct_index": correct_index,
            "explanation": "This answer is grounded in a passage from your uploaded source.",
        })
    return questions

def gemini_questions(chunks, count, api_key, model):
    """Generate varied, source-grounded quiz questions with Gemini REST."""
    evidence_parts = []
    for chunk in chunks:
        cleaned = re.sub(r"\s+", " ", chunk.content).strip()[:1800]
        evidence_parts.append(f"[Page {chunk.page}] {cleaned}")
    evidence = "\n\n".join(evidence_parts)
    schema = {
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "question": {"type": "STRING"},
                "options": {"type": "ARRAY", "items": {"type": "STRING"}},
                "correct_index": {"type": "INTEGER"},
                "explanation": {"type": "STRING"},
            },
            "required": ["question", "options", "correct_index", "explanation"],
        },
    }
    prompt = f"""You are the quiz designer inside StudyForge.
Create exactly {count} challenging but fair multiple-choice questions from ONLY the evidence below.
Make every question different. Test a mix of definition, application, comparison, and recall.
Each question must have exactly 4 plausible options, one correct answer, and correct_index must be 0, 1, 2, or 3.
Do not mention that you are an AI. Do not invent facts outside the evidence.

EVIDENCE:
{evidence}"""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.75,
            "responseMimeType": "application/json",
            "responseSchema": schema,
        },
    }
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    request = urlrequest.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )
    try:
        with urlrequest.urlopen(request, timeout=45) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (urlerror.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Gemini request failed: {exc}") from exc

    try:
        text = body["candidates"][0]["content"]["parts"][0]["text"]
        questions = json.loads(text)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Gemini returned an unexpected quiz response") from exc

    valid = []
    for item in questions:
        options = item.get("options", [])
        correct_index = item.get("correct_index")
        if isinstance(item.get("question"), str) and len(options) == 4 and isinstance(correct_index, int) and 0 <= correct_index < 4:
            valid.append({
                "question": item["question"],
                "options": [str(option) for option in options],
                "correct_index": correct_index,
                "explanation": str(item.get("explanation", "Grounded in your uploaded source.")),
            })
    if len(valid) < count:
        raise RuntimeError("Gemini returned too few valid questions")
    return valid[:count]

def gemini_chat(chunks, question, history, api_key, model):
    """Answer as a natural, emotionally intelligent study companion grounded in retrieved pages."""
    evidence_parts = []
    for chunk in chunks:
        cleaned = re.sub(r"\s+", " ", chunk.content).strip()[:1800]
        evidence_parts.append(f"[Page {chunk.page}] {cleaned}")
    evidence = "\n\n".join(evidence_parts)
    contents = []
    for item in history[-10:]:
        role = "model" if item.get("role") in {"ai", "model"} else "user"
        contents.append({"role": role, "parts": [{"text": str(item.get("text", ""))[:4000]}]})
    contents.append({"role": "user", "parts": [{"text": question}]})
    payload = {
        "systemInstruction": {"parts": [{"text": """You are Mira, a real-feeling study companion inside StudyForge: part close friend, part patient teacher, part thoughtful mentor.
Talk like a warm human who knows the student, not like a document-search tool. Use natural contractions, varied sentence length, gentle humor when appropriate, and genuine curiosity. Never begin with phrases like "Here's the clearest piece of evidence I found" or "Based on your source" unless the student specifically asks for sources.
Answer the student's actual message before turning it into a lesson. For greetings, feelings, motivation, planning, and casual conversation, respond naturally and do not force the PDF into the conversation. Remember the recent conversation and refer back to it like a real tutor would.
When teaching, explain one idea clearly, use a relatable example, then ask one small question to keep the student involved. When the student is confused, slow down and reassure them without sounding scripted. When they ask for advice, give a concrete next action. When they ask to pick a chapter, recommend a chapter from the evidence with a human reason, then invite them to start.
If they ask for a recap, use crisp bullets. If they ask to be quizzed, ask one question at a time and wait for their answer. Never invent facts. If the notes do not contain the answer, say naturally that you cannot find it in these notes and ask what they would like to do next.
Do not add page citations, evidence labels, or machine-like headings to normal conversation. Sources are displayed separately in the interface. Keep normal answers under 250 words and make each reply feel specific to this student."""}]},
        "contents": contents,
        "generationConfig": {"temperature": 0.8, "maxOutputTokens": 700},
    }
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    request = urlrequest.Request(endpoint, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type":"application/json", "x-goog-api-key":api_key}, method="POST")
    try:
        with urlrequest.urlopen(request, timeout=45) as response:
            body = json.loads(response.read().decode("utf-8"))
        return body["candidates"][0]["content"]["parts"][0]["text"]
    except (urlerror.URLError, TimeoutError, json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Gemini tutor request failed: {exc}") from exc

def coach_answer(chunks, question):
    """Useful local tutor fallback for development without a Gemini key."""
    lowered = question.lower().strip()
    if lowered in {"hi", "hello", "hey", "hi mira", "hello mira", "hey mira"} or any(phrase in lowered for phrase in ("how are you", "how're you", "who are you", "good morning", "good evening")):
        return "Hi! I’m Mira 🌱 I’m here to help you understand your notes, remember them, and practice without making studying feel heavy. Try asking me to explain a concept, make a memory trick, or quiz you."
    if not chunks:
        return "I’m ready to help, but I couldn’t find enough evidence in this source. Try asking about a heading, keyword, or concept from the PDF."

    passages = [re.sub(r"\s+", " ", re.sub(r"\[?Page\s+\d+\]?", "", chunk.content, flags=re.I)).strip() for chunk in chunks[:4]]
    if any(phrase in lowered for phrase in ("pick a chapter", "pick one chapter", "choose a chapter", "which chapter", "what should i study", "what do i study", "study next")):
        chapter_pattern = re.compile(r"\b(?:chapter|unit|module|section)\s+(?:[0-9]+|[ivxlcdm]+)\b[^.!?\n]{0,90}", re.I)
        candidates = []
        for chunk in chunks:
            for match in chapter_pattern.findall(chunk.content):
                label = re.sub(r"\s+", " ", match).strip(" :-")
                if label.lower() not in {item[0].lower() for item in candidates}:
                    candidates.append((label, chunk.page))
        if candidates:
            chosen = candidates[0]
            options = "\n".join(f"{index + 1}. {label} [Page {page}]" for index, (label, page) in enumerate(candidates[:6]))
            return f"Yes—we can absolutely do that. I’d start with **{chosen[0]}** because it looks like a foundation chapter, and I’d rather make sure that base is solid before we jump ahead.\n\nI can also see:\n{options}\n\nWant to start with {chosen[0]}? I’ll explain the big picture first, give you a simple example, and then ask one quick question to see where you’re at. If you’re studying a different chapter for an exam, tell me and I’ll switch gears."
        return "Yes—we can choose one together. I can see the source, but its chapter headings are not clear enough for me to name one responsibly. Tell me the chapter numbers or paste the table of contents, and I’ll recommend the best starting point based on foundations and your exam goal."
    if "10 points" in lowered or "ten points" in lowered or any(word in lowered for word in {"bullet", "summary", "summarise", "summarize", "revise", "revision"}):
        sentences = []
        for passage in passages:
            sentences.extend(re.split(r"(?<=[.!?])\s+", passage))
        bullets = [sentence.strip() for sentence in sentences if len(sentence.strip()) > 25][:10]
        return "Okay, let’s turn this into something you can actually remember.\n\n" + "\n".join(f"• {bullet}" for bullet in bullets) + "\n\nNow cover the notes and try to rebuild the list in 60 seconds. I’ll help you with whichever point disappears first."
    if any(phrase in lowered for phrase in ("15-minute", "15 minute", "practice-first", "practice first", "study move", "what should i do")):
        idea = passages[0][:220]
        return f"Absolutely. Here’s your 15-minute move:\n\n1. Spend 3 minutes reading this idea: {idea}\n2. Close the notes and explain it out loud in your own words.\n3. Spend 7 minutes making one example or solving one small problem.\n4. Use the last 2 minutes to write down the part that still feels shaky.\n\nSend me that shaky part and I’ll coach you through it."
    if "quiz" in lowered or "test me" in lowered:
        return f"Alright, let’s see what you already know—no pressure.\n\nWhat’s the main idea here, in your own words? Don’t worry about making it perfect. I’ll help you sharpen it after you answer."
    if "trick" in lowered or "remember" in lowered or "memor" in lowered:
        keyword = passages[0].split()[0] if passages[0].split() else "this idea"
        return f"Let’s make this stick. Picture **{keyword}** as a tiny scene or story in your head—something strange or funny works best. Then connect it to one example from your own life.\n\nTry explaining the idea back to me in one sentence, and I’ll tell you what you’ve got right and what to strengthen."
    return f"I think the important idea here is this: {passages[0][:500]}\n\nLet’s not just read it and move on. Tell me what you think it means in your own words—even if you’re unsure. I’ll help you untangle it from there."
