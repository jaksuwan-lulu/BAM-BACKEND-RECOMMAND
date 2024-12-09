from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from app.utils.jwt_handler import verify_access_token_from_cookie
from app.database.database import get_database

router = APIRouter()

class EditProfileRequest(BaseModel):
    name: str
    surname: str
    number: str

@router.get("/view-profile")
async def view_profile(request: Request, db=Depends(get_database)):
    """
    ดึงข้อมูลโปรไฟล์ผู้ใช้ โดยตรวจสอบ access_token จาก HTTP-only cookies
    """
    token_data = verify_access_token_from_cookie(request)
    user_email = token_data['sub']

    user = db["users"].find_one({"email": user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"name": user["name"], "surname": user["surname"], "number": user["number"]}

@router.post("/edit-profile")
async def edit_profile(request: Request, profile_request: EditProfileRequest, db=Depends(get_database)):
    """
    อัปเดตโปรไฟล์ผู้ใช้ โดยตรวจสอบ access_token จาก HTTP-only cookies
    """
    token_data = verify_access_token_from_cookie(request)
    user_email = token_data['sub']

    result = db['users'].update_one(
        {"email": user_email},
        {"$set": {
            "name": profile_request.name,
            "surname": profile_request.surname,
            "number": profile_request.number
        }}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "Profile updated successfully"}

@router.post("/add-favorite")
async def toggle_favorite(request: Request, asset_id: str, db=Depends(get_database)):
    """
    เพิ่มหรือลบบ้านจากรายการโปรด โดยตรวจสอบ access_token จาก HTTP-only cookies
    """
    token_data = verify_access_token_from_cookie(request)
    user_email = token_data['sub']

    # ตรวจสอบว่า asset_id มีอยู่ใน collection 'preProcessed_500' หรือไม่
    asset = db['preProcessed_500'].find_one({"asset_id": asset_id})
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # ตรวจสอบว่ารายการนี้มีอยู่แล้วใน collection 'favorite'
    existing_favorite = db['favorite'].find_one({"email": user_email, "asset_id": asset_id})

    if existing_favorite:
        db['favorite'].delete_one({"email": user_email, "asset_id": asset_id})
        return {"message": "House removed from favorite list"}
    else:
        favorite = {
            "email": user_email,
            "asset_id": asset_id
        }
        db['favorite'].insert_one(favorite)
        return {"message": "House added to favorite list"}
