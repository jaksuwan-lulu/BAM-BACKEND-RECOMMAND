from fastapi import APIRouter, HTTPException, Response, Request, Depends
from pydantic import BaseModel
from passlib.context import CryptContext
from app.database.database import get_database
from app.utils.jwt_handler import create_access_token, create_refresh_token, verify_access_token
from app.models.models import BlacklistToken
from datetime import datetime

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
        # หากไม่มี access token ใน cookies ให้แจ้งว่าไม่อนุญาต
        raise HTTPException(status_code=401, detail="Access token is missing or invalid")

    # ตรวจสอบว่า token ถูกต้องหรือไม่
    try:
        payload = verify_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid access token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    try:
        # เพิ่ม token ลงใน Blacklist
        blacklist_entry = {
            "token_key": token,
            "is_logout": True,
            "updated_time": datetime.utcnow()  # ใช้เวลา UTC
        }
        db["blacklist_token"].insert_one(blacklist_entry)

        # ลบ cookies ทั้ง access token และ refresh token
        response.delete_cookie(key="access_token", httponly=True)
        response.delete_cookie(key="refresh_token", httponly=True)

        return {"message": "User has been logged out successfully"}
    except Exception as e:
        # กรณีที่เพิ่ม token ลง blacklist ไม่สำเร็จ
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")


# Middleware or helper for handling refresh token when access token expired
@router.get("/protected-resource")
async def protected_resource(request: Request):
    # ดึง access_token จาก Cookies
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token is missing")

    try:
        # เรียก verify_access_token โดยไม่ใช้อาร์กิวเมนต์ raise_expired
        payload = verify_access_token(access_token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # ใช้ payload ที่ตรวจสอบแล้ว
    return {"message": "You have accessed a protected resource", "user": payload["sub"]}
