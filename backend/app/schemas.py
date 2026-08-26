from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
class Signup(BaseModel): email: EmailStr; password: str = Field(min_length=8); name: str
class Login(BaseModel): email: EmailStr; password: str
class Token(BaseModel): access_token: str; token_type: str = "bearer"
class UserOut(BaseModel): id:int; email:EmailStr; name:str; xp:int; streak:int; learning_style:str|None=None; goals:list=[]
class Onboarding(BaseModel): goals:list[str]; learning_style:str
class ChatMessage(BaseModel): role:str; text:str = Field(max_length=4000)
class ChatRequest(BaseModel): document_id:int; question:str = Field(min_length=2, max_length=2000); history:list[ChatMessage] = Field(default_factory=list)
class QuizRequest(BaseModel): document_id:int; count:int=Field(default=5, ge=1, le=10)
class QuizAnswer(BaseModel): correct_index:int
class QuizSubmit(BaseModel): document_id:int; answers:list[QuizAnswer]; questions:list[dict]
class PlanRequest(BaseModel): exam_date:str; minutes_per_day:int=Field(ge=15,le=600); subject:str; education_level:str = "Undergraduate"
