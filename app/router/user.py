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

