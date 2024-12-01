import jwt
import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from app.database.database import get_database

# กำหนดค่าการเข้ารหัส
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # เวลา Access Token หมดอายุ (30 นาที)
REFRESH_TOKEN_EXPIRE_MINUTES = 1440  # เวลา Refresh Token หมดอายุ (1 วัน)

db = get_database()

# ตรวจสอบว่ามี token อยู่ใน blacklist หรือไม่
def is_token_blacklisted(token: str):
    blacklist_entry = db['blacklist_token'].find_one({"token_key": token})
    return blacklist_entry is not None

# สร้าง Access Token
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({
        "exp": expire,
        "unique_id": str(uuid.uuid4())
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# สร้าง Refresh Token
def create_refresh_token(data: dict, expires_delta: timedelta = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({
        "exp": expire,
        "unique_id": str(uuid.uuid4())
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ตรวจสอบ Access Token
def verify_access_token(token: str):
    """
    ตรวจสอบความถูกต้องของ access token
    """
    try:
        # ตรวจสอบว่า token อยู่ใน Blacklist หรือไม่
        if is_token_blacklisted(token):
            raise HTTPException(status_code=401, detail="Token has been revoked")
        
        # ถอดรหัสและตรวจสอบ JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=401, detail="Token signature is invalid")
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Token decoding failed")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        # จัดการข้อผิดพลาดที่ไม่ได้คาดการณ์ไว้
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# ตรวจสอบ Access Token จาก HTTP-only Cookie
def verify_access_token_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Access token is missing")
    try:
        if is_token_blacklisted(token):
            raise HTTPException(status_code=401, detail="Token has been revoked")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
