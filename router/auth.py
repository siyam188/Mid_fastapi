from fastapi import FastAPI,APIRouter,Depends,HTTPException
from pydantic import BaseModel
from model import Users
from typing import Annotated,Optional,Literal
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from datetime import timedelta, datetime, timezone
from jose import jwt,JWTError


router=APIRouter(prefix="/auth")
bcrpt_context =CryptContext(  schemes=["bcrypt"], deprecated="auto")
Auth2_Bearer = OAuth2PasswordBearer(
    tokenUrl="/auth/login")

SECRET_KEY = "replace_with_your_random_secret_key"
ALGORITHM = "HS256"

def create_access_token(
    username: str,
    user_id: int,
    expires_delta: timedelta
):
    encode = {
        "sub": username,
        "id": user_id
    }

    expire = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expire})

    return jwt.encode(
        encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
def get_current_user(
    token: Annotated[str, Depends(Auth2_Bearer)]
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")
        user_id = payload.get("id")

        if username is None or user_id is None:
            raise HTTPException(
                status_code=401,
                detail="User not Found"
            )

        return {
            "username": username,
            "id": user_id
        }

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


class createusers(BaseModel):
    username:str
    email:str
    password:str


def Authenticate_User(username, password, db):
    user = db.query(Users).filter(Users.username == username ).first()

    if user is None:
        return False

    if bcrpt_context.verify(password, user.hash_password):
        return user

    return False

def get_db():
    db=SessionLocal()
    try:
         yield db
    finally:
        db.close()


db_depends=Annotated[Session,Depends(get_db)]




@router.post('/register')
def create_users(db:db_depends,new_user=createusers):
    user_model=Users(
        email=new_user.email,
        username=new_user.username,
        hash_password=bcrpt_context.hash(new_user.password)
    )
    db.add(user_model)
    db.commit()

    return JSONResponse(
        status_code=202,
        content="User_Create Done"
    )
@router.post("/login")
def login_user(db:db_depends, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = Authenticate_User(
        form_data.username,
        form_data.password,
        db
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Fail"
        )

    token = create_access_token(
        user.username,
        user.id,
        timedelta(minutes=30)
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }
