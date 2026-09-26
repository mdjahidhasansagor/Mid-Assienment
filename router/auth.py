from fastapi import FastAPI, APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from models import User
from datetime import timedelta, datetime, timezone
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from database import engine, sessionLocal
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError


router = APIRouter()

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
OAuth2_bearer = OAuth2PasswordBearer(tokenUrl='/auth/login')

SECRET_KEY = '5b70dc4b0006fdf65224e06aa2edb30c4f00b02ea1e85dc48ee4ea2997edf4ac'
ALGORITHM = 'HS256'


class CreateUser(BaseModel):
    
    username : str
    email : str
    password : str

def authenticate_user(username, password, db):
    user = db.query(User).filter(User.username == username).first()

    if user is None:
        return False
    if bcrypt_context.verify(password, user.hashed_password):
        return user
    return False


def create_access_token(username : str, user_id : int, expires_delta : timedelta):
    encode = {'sub' : username, 'id' : user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp' : expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token : Annotated[str, Depends(OAuth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username : str = payload.get('sub')
        user_id : int = payload.get('id')

        if username is None or user_id is None:
            raise HTTPException(status_code=404, detail='User not found!')
        return {'username' : username, 'id' : user_id}
    except:
        raise HTTPException(status_code=404, detail='User not found!')


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post('/auth/register')
def register_user(db : db_dependency, new_user : CreateUser):
    user_model = User(
        username = new_user.username,
        email = new_user.email,
        hashed_password = bcrypt_context.hash(new_user.password)
    )

    db.add(user_model)
    db.commit()

    return JSONResponse(status_code=201, content={'massage' : 'User create successfully!'})


@router.post('/auth/login')
def login_user(db : db_dependency, from_data : Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(from_data.username, from_data.password, db)

    if not user:
        raise HTTPException(status_code=404, detail='Faield Authenticated')

    token = create_access_token(user.username, user.id, timedelta(minutes=30))
    return {'access_token' : token, 'token_type' : 'bearer'}