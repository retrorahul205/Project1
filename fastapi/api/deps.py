from typing import Annotated;
from sqlalchemy.orm import Session
from fastapi import HttpException, status , Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from dotenv import load_dotenv
import os
from .database import SessionLocal

load_dotenv()

SECRET_KEY = os.getenv("AUTH_SECRET_KEY")
ALGORITHM = os.getenv("AUTH_ALGORITHM")

def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:   
        db.close()

db_dependency: Annotated[Session, Depends(get_db)]
brcypt_context= CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer= OAuth2PasswordBearer(tokenUrl="auth/token")
oauth2_beared_dependency: Annotated[str, Depends(oauth2_bearer)]

async def get_current_user(token: oauth2_beared_dependency):
    try:
        payload= jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str= payload.get("sub")
        user_id: str= payload.get("id")
        if username is None or user_id is None:
            raise HttpException(statuc_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate credentials",)
        return {"username": username, "id": user_id}

    except JWTError:
        raise HttpException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials",)
    
user_dependency: Annotated[dict, Depends(get_current_user)]
    
