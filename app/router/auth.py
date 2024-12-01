from fastapi import APIRouter, HTTPException, Depends, Form, Response, Request
from pydantic import BaseModel
from passlib.context import CryptContext
from app.database.database import get_database
from app.utils.jwt_handler import create_access_token, create_refresh_token, verify_access_token
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer
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

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login(response: Response, request: LoginRequest):
    db_user = db['users'].find_one({"email": request.email})
    if not db_user or not pwd_context.verify(request.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    # สร้าง access token และ refresh token
    access_token = create_access_token(data={"sub": db_user["email"]})
    refresh_token = create_refresh_token(data={"sub": db_user["email"]})

    # ตั้งค่า HTTP-only cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="Lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="Lax"
    )

    return {"message": "Login successful"}

@router.post("/logout")
async def logout(response: Response, request: Request):
    # ดึง HTTP-only access token จาก cookies
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Access token is missing or invalid")

    # ตรวจสอบว่ามี token ใน cookies หรือไม่
    try:
        # เพิ่ม token ลงใน Blacklist (หรือจัดการตามการออกแบบระบบ)
        blacklist_entry = BlacklistToken(token_key=token, is_logout=True)
        blacklist_entry.save()

        # ลบ cookies ทั้ง access token และ refresh token
        response.delete_cookie(key="access_token", httponly=True)
        response.delete_cookie(key="refresh_token", httponly=True)

        return {"message": "User has been logged out successfully"}
    except Exception as e:
        # ในกรณีที่เกิดปัญหา ให้ส่งกลับ error
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")


@router.post("/token")
async def token(username: str = Form(...), password: str = Form(...)):
    db_user = db['users'].find_one({"email": username})
    if not db_user or not pwd_context.verify(password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # สร้าง access token และ refresh token
    access_token = create_access_token(data={"sub": db_user["email"]})
    refresh_token = create_refresh_token(data={"sub": db_user["email"]})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh-token")
async def refresh_token(response: Response, request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token is missing")
    
    payload = verify_access_token(refresh_token)
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
        secure=False,
        samesite="Lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,
        samesite="Lax"
    )

    return {"message": "Tokens refreshed successfully"}
