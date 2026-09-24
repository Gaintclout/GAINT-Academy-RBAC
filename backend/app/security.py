import datetime as dt
from typing import Optional, Iterable
from fastapi import Depends, Header, HTTPException
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .config import settings
from .database import get_db
from .models import User

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(value: str) -> str:
    return pwd.hash(value)

def verify_password(value: str, hashed: str) -> bool:
    return pwd.verify(value, hashed)

def create_token(user: User) -> str:
    exp = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    return jwt.encode(
        {
            "sub": str(user.id),
            "tenant": user.tenant_id,
            "campus": user.campus_id,
            "role": user.role,
            "email": user.email,
            "exp": exp,
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

def current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Authentication required")
    try:
        payload = jwt.decode(
            authorization[7:],
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user = db.get(User, int(payload["sub"]))
    except (JWTError, ValueError, TypeError, KeyError):
        raise HTTPException(401, "Invalid or expired token")
    if not user or not user.is_active:
        raise HTTPException(401, "User not found or inactive")
    return user

def require_roles(*roles: str):
    def dep(user: User = Depends(current_user)):
        if user.role not in roles:
            raise HTTPException(403, "You do not have permission for this action")
        return user
    return dep
