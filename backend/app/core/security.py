from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"

def hash_password(password: str) -> str: return pwd_context.hash(password)
def verify_password(password: str, hashed: str) -> bool: return pwd_context.verify(password, hashed)
def create_access_token(subject: str) -> str:
    return jwt.encode({"sub": subject, "exp": datetime.now(timezone.utc) + timedelta(days=7)}, settings.secret_key, algorithm=ALGORITHM)
