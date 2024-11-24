import jwt
import uuid  # นำเข้า uuid สำหรับสร้าง unique_id
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.database.database import get_database

SECRET_KEY = "your_secret_key"  # กำหนด Secret key สำหรับการเข้ารหัส
ALGORITHM = "HS256"  # ใช้ HS256 ในการเข้ารหัส
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # เวลา Access Token หมดอายุ (30 นาที)
REFRESH_TOKEN_EXPIRE_MINUTES = 1440  # เวลา Refresh Token หมดอายุ (1 วัน)

db = get_database()

# ฟังก์ชันตรวจสอบว่ามี token อยู่ใน blacklist หรือไม่
def is_token_blacklisted(token: str):
    blacklist_entry = db['blacklist_token'].find_one({"token_key": token})
    return blacklist_entry is not None

# สร้าง Access Token
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({
        "exp": expire,
        "unique_id": str(uuid.uuid4())  # เพิ่ม unique_id เพื่อความแตกต่าง
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# สร้าง Refresh Token
def create_refresh_token(data: dict, expires_delta: timedelta = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({
        "exp": expire,
        "unique_id": str(uuid.uuid4())  # เพิ่ม unique_id เพื่อความแตกต่าง
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ตรวจสอบ Access Token
def verify_access_token(token: str):
    try:
        # ตรวจสอบว่า token นี้อยู่ใน blacklist หรือไม่
        if is_token_blacklisted(token):
            raise HTTPException(status_code=401, detail="Token has been revoked")

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
