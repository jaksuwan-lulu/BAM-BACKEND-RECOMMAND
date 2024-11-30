from fastapi import APIRouter, HTTPException, Depends, Form, Response
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
async def login(response: Response, email: str = Form(...), password: str = Form(...)):
    db_user = db['users'].find_one({"email": email})
    if not db_user or not pwd_context.verify(password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    # สร้าง access token และ refresh token
    access_token = create_access_token(data={"sub": db_user["email"]})
    refresh_token = create_refresh_token(data={"sub": db_user["email"]})
    
    # ตั้งค่า HTTP-only cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # ใช้ secure=True หากคุณใช้ HTTPS
        samesite="Lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="Lax"
    )
    
    return {"message": "Login successful"}

@router.post("/logout")
async def logout(response: Response, token: str = Depends(oauth2_scheme)):
    token_data = verify_access_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # บันทึก token ลงใน blacklist
    blacklist_entry = BlacklistToken(token_key=token, is_logout=True)
    blacklist_entry.save()

    # ลบ cookies
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return {"message": "User has been logged out successfully"}

@router.post("/refresh-token")
async def refresh_token(response: Response, token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user_email = payload['sub']

    # สร้าง access token และ refresh token ใหม่
    new_access_token = create_access_token(data={"sub": user_email})
    new_refresh_token = create_refresh_token(data={"sub": user_email})

    # ตั้งค่า HTTP-only cookies ใหม่
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=True,
        samesite="Lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="Lax"
    )

    return {"message": "Tokens refreshed successfully"}
