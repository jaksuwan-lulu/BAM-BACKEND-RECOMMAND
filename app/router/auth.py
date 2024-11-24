from fastapi import APIRouter, HTTPException, Depends, Form , Request
from pydantic import BaseModel
from passlib.context import CryptContext
from app.database.database import get_database
from app.utils.jwt_handler import create_access_token, create_refresh_token, verify_access_token
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer
import uuid
from app.models.models import BlacklistToken

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

db = get_database()

class UserRegister(BaseModel):
    email: str
    password: str
    name: str
    surname: str
    number: str = None

class TokenRefreshRequest(BaseModel):
    refresh_token: str

@router.post("/register")
async def register(user: UserRegister):
    db_user = db['users'].find_one({"email": user.email})
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = pwd_context.hash(user.password)
    new_user = {
        "email": user.email,
        "password": hashed_password,
        "name": user.name,
        "surname": user.surname,
        "number": user.number
    }
    db['users'].insert_one(new_user)
    return {"message": "User created successfully"}

@router.post("/login")
async def login(email: str = Form(...), password: str = Form(...)):
    db_user = db['users'].find_one({"email": email})
    if not db_user or not pwd_context.verify(password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    # สร้าง access token และ refresh token
    access_token = create_access_token(data={"sub": db_user["email"]})
    refresh_token = create_refresh_token(data={"sub": db_user["email"]})
    
    return {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,  # เพิ่ม refresh token ใน response
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    token_data = verify_access_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # บันทึก token ลงใน blacklist
    blacklist_entry = BlacklistToken(token_key=token, is_logout=True)
    blacklist_entry.save()

    return {"message": "User has been logged out successfully"}

@router.post("/token")
async def token(username: str = Form(...), password: str = Form(...)):
    db_user = db['users'].find_one({"email": username})
    if not db_user or not pwd_context.verify(password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": db_user["email"], "unique_id": str(uuid.uuid4())})
    refresh_token = create_refresh_token(data={"sub": db_user["email"], "unique_id": str(uuid.uuid4())})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh-token")
async def refresh_token(request: TokenRefreshRequest):
    payload = verify_access_token(request.refresh_token)  # แก้ไขให้เหลือ argument เดียว
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user_email = payload['sub']

    # สร้าง access token และ refresh token ใหม่
    new_access_token = create_access_token(data={"sub": user_email})
    new_refresh_token = create_refresh_token(data={"sub": user_email})

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }
