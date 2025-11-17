
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os

from database import get_db
from models import User

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 dana

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifikacija password-a"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password-a"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Kreiranje JWT tokena"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Dobijanje trenutnog korisnika iz JWT tokena"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    print(f"🔍 DEBUG - Received token: {token[:50]}...")  # DEBUG
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"🔍 DEBUG - Decoded payload: {payload}")  # DEBUG
        
        user_id = payload.get("sub")
        print(f"🔍 DEBUG - User ID from token: {user_id}, Type: {type(user_id)}")  # DEBUG
        
        if user_id is None:
            print("❌ DEBUG - user_id is None!")  # DEBUG
            raise credentials_exception
            
        # Ensure user_id is int
        user_id = int(user_id)
        print(f"🔍 DEBUG - Converted user_id to int: {user_id}")  # DEBUG
        
    except (JWTError, ValueError) as e:
        print(f"❌ DEBUG - JWT/Value Error: {e}")  # DEBUG
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    print(f"🔍 DEBUG - Found user in DB: {user}")  # DEBUG
    
    if user is None:
        print(f"❌ DEBUG - No user with ID {user_id} in database!")  # DEBUG
        raise credentials_exception
    
    print(f"✅ DEBUG - Returning user: {user.username}")  # DEBUG
    return user