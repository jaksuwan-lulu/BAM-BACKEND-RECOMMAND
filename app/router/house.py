from fastapi import APIRouter, Depends, HTTPException
from pymongo import MongoClient
from app.utils.jwt_handler import verify_access_token
from app.database.database import get_database
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

router = APIRouter()
db = get_database()  # ดึงฐานข้อมูลจาก get_database()

@router.get("/")
async def get_houses(db=Depends(get_database)):
    houses_cursor = db["preProcessed_500"].find()
    houses = []
    for house in houses_cursor:
        del house['_id']  # ลบฟิลด์ _id ออกจากผลลัพธ์
        houses.append(house)
    return houses

@router.get("/search")
async def search_houses(query: str, db=Depends(get_database)):
    houses = db['preProcessed_500'].find({"asset_project_name": {"$regex": query, "$options": "i"}})
    
    result = []
    for house in houses:
        del house['_id']  # ลบฟิลด์ _id ออกจากผลลัพธ์
        result.append(house)
    return result

@router.get("/getdetail")
async def get_house_detail(house_id: str, db=Depends(get_database)):
    """
    รับ house_id จาก Frontend และส่งข้อมูลบ้านที่ตรงกับ house_id กลับไป
    """
    house = db["preProcessed_500"].find_one({"id": house_id})  # ค้นหาโดย id
    if not house:
        raise HTTPException(status_code=404, detail="House not found")

    del house['_id']  # ลบฟิลด์ _id ออกจากผลลัพธ์เพื่อหลีกเลี่ยงข้อผิดพลาด serialization
    return house
