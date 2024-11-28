from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.utils.jwt_handler import verify_access_token
from fastapi.security import OAuth2PasswordBearer
from app.database.database import get_database  # นำเข้า get_database เพื่อใช้งาน

router = APIRouter()

# เพิ่มการนิยาม oauth2_scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class EditProfileRequest(BaseModel):
    name: str
    surname: str
    number: str

@router.get("/users/view-profile")
async def view_profile(token: str = Depends(oauth2_scheme), db=Depends(get_database)):
    # ถอดรหัสและตรวจสอบ token เพื่อดึง payload
    payload = verify_access_token(token)  # ส่งแค่ argument เดียว
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_email = payload['sub']
    user = db['users'].find_one({"email": user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"name": user["name"], "surname": user["surname"], "number": user["number"]}

@router.post("/users/edit-profile")
async def edit_profile(request: EditProfileRequest, token: str = Depends(oauth2_scheme), db=Depends(get_database)):
    # ถอดรหัสและตรวจสอบ token เพื่อดึง payload
    payload = verify_access_token(token)  # ส่งแค่ argument เดียว
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_email = payload['sub']
    result = db['users'].update_one(
        {"email": user_email},
        {"$set": {
            "name": request.name,
            "surname": request.surname,
            "number": request.number
        }}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "Profile updated successfully"}

@router.post("/users/add-favorite")
async def toggle_favorite(asset_id: str, token: str = Depends(oauth2_scheme)):
    db = get_database()  # เรียกใช้ฐานข้อมูลภายในฟังก์ชัน
    token_data = verify_access_token(token)  # ส่งแค่ token อย่างเดียว

    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_email = token_data['sub']  # ดึงค่า email จาก token

    # ตรวจสอบว่า asset_id มีอยู่ใน collection 'preProcessed_500' หรือไม่
    asset = db['preProcessed_500'].find_one({"asset_id": asset_id})
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # ตรวจสอบว่ารายการนี้มีอยู่แล้วใน collection 'favorite'
    existing_favorite = db['favorite'].find_one({"email": user_email, "asset_id": asset_id})
    
    if existing_favorite:
        # ถ้ามีอยู่แล้ว ให้ลบรายการออก
        db['favorite'].delete_one({"email": user_email, "asset_id": asset_id})
        return {"message": "House removed from favorite list"}
    else:
        # ถ้าไม่มี ให้เพิ่มรายการใหม่
        favorite = {
            "email": user_email,
            "asset_id": asset_id
        }
        db['favorite'].insert_one(favorite)
        return {"message": "House added to favorite list"}
