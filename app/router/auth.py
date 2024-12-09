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
        samesite="None"  
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  
        samesite="None"
    )

    return {"message": "Login successful"}

@router.post("/logout")
async def logout(response: Response, request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Access token is missing or invalid")

    try:
        payload = verify_access_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    blacklist_entry = {
        "token_key": token,
        "is_logout": True,
        "updated_time": datetime.utcnow()
    }
    db["blacklist_token"].insert_one(blacklist_entry)

    response.delete_cookie(key="access_token", httponly=True, samesite="None")
    response.delete_cookie(key="refresh_token", httponly=True, samesite="None")

    return {"message": "User has been logged out successfully"}

@router.get("/status")
async def get_status(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return {"status": "logged_out", "message": "No access token found."}

    blacklisted_token = db["blacklist_token"].find_one({"token_key": token})
    if blacklisted_token:
        return {"status": "logged_out", "message": "Token has been revoked."}

    try:
        payload = verify_access_token(token)
        return {"status": "logged_in", "user": payload["sub"]}
    except HTTPException as e:
        return {"status": "logged_out", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}

@router.get("/protected-resource")
async def protected_resource(request: Request):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token is missing")

    try:
        payload = verify_access_token(access_token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    return {"message": "You have accessed a protected resource", "user": payload["sub"]}
