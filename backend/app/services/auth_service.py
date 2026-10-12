from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password

def register_user(db: Session, user_in: UserCreate) -> User:
    """Create a new user account with hashed password after checking email uniqueness."""
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )
    
    hashed = hash_password(user_in.password)
    user = User(
        email=user_in.email,
        hashed_password=hashed,
        full_name=user_in.full_name,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Verify user credentials and return User object if valid, else None."""
    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
