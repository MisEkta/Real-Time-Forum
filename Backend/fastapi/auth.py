from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import shutil
from pathlib import Path
from ..database.database import get_db
from ..database.models import User as UserModel

router = APIRouter()

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
UPLOAD_DIR = Path("uploads/profile_images")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

class User(BaseModel):
    name: str
    email: str
    password: str

class UserInDB(User):
    id: int
    hashed_password: str
    profile_image: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Session, username: str = None, email: str = None):
    if username:
        return db.query(UserModel).filter(UserModel.name == username).first()
    if email:
        return db.query(UserModel).filter(UserModel.email == email).first()
    return None

def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register", response_model=UserInDB)
def register(
    user: User,
    db: Session = Depends(get_db)
):
    hashed_password = get_password_hash(user.password)
    
    db_user = UserModel(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        profile_image=None  # Default to None
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserInDB(
        id=db_user.id,
        name=db_user.name,
        email=db_user.email,
        password=user.password,
        hashed_password=db_user.hashed_password,
        profile_image=db_user.profile_image
    )

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

@router.put("/update-password")
def update_password(password: str, new_password: str, db: Session = Depends(get_db), current_user: UserInDB = Depends(get_current_user)):
    if not verify_password(password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this password since password is incorrect.")
    else:
        hashed_password = get_password_hash(new_password)
        db.query(UserModel).update({"hashed_password": hashed_password})
        db.commit()
        
        return {"message": "Password updated successfully"}