from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from backend.app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from backend.app.database import get_session
from backend.app.models import Token, User, UserCreate

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=Token)
def register(user_in: UserCreate, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == user_in.username)).first()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")

    db_user = User(
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        role="user",
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    access_token = create_access_token(subject=db_user.username)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(subject=user.username)
    return {"access_token": access_token, "token_type": "bearer"}
