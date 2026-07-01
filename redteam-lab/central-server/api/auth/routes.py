from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database.db import get_db, User
from api.auth.utils import hash_password, verify_password, create_access_token

router = APIRouter()


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token({"sub": user.id, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "role": user.role}


@router.get("/me")
def me(db: Session = Depends(get_db)):
    # handled via dependency in real calls; this is just a placeholder
    return {"detail": "use Authorization: Bearer <token>"}
