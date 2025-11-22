from datetime import datetime, timedelta, timezone 
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from dotenv import load_dotenv
import os
from api.models import User
from api.deps import (
    db_dependency,
    brcypt_context
)

load_dotenv()

router=APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY= os.getenv("AUTH_SECRET_KEY")
ALGORITHM= os.getenv("AUTH_ALGORITHM")


class UserCreateRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


def authenticate_user(db, username: str, password: str):
    user= db.query(User).filter(User.username== username).first()
    if not user:
        return False
    if not brcypt_context.verify(password, user.hashed_password):
        return False
    return user 
def create_access_token(username: str, expires_delta: timedelta):
    encode ={'sub': username,'id':user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)  

@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_user(user_request: UserCreateRequest, db: db_dependency):
    create_user_model=User(
        username=user_request.username,
        hashed_password= brcypt_context.hash(user_request.password)
    )
    db.add(create_user_model)
    db.commit()

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency
):
    user= authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires= timedelta(minutes=30)
    access_token= create_access_token(
        username=user.username,
        expires_delta= access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}