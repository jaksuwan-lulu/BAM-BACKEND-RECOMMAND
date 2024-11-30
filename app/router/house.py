from fastapi import APIRouter, Depends, HTTPException, Request
from app.utils.jwt_handler import verify_access_token_from_cookie
from app.database.database import get_database
from app.models.models import FavoriteHouses

router = APIRouter()

db = get_database()  # ดึงฐานข้อมูลจาก get_database()

@router.get("/")
async def get_houses(db=Depends(get_database)):
    """
    ดึงข้อมูลบ้านทั้งหมดจาก collection preProcessed_500
    """
    houses_cursor = db["preProcessed_500"].find()
    houses = []
    for house in houses_cursor:
        del house['_id']  # ลบฟิลด์ _id ออกจากผลลัพธ์
        houses.append(house)
    return houses

@router.get("/search")
async def search_houses(query: str, db=Depends(get_database)):
    """
    ค้นหาบ้านตามชื่อโครงการ (asset_project_name)
    """
    houses = db['preProcessed_500'].find({"asset_project_name": {"$regex": query, "$options": "i"}})
    
    result = []
    for house in houses:
        del house['_id']  # ลบฟิลด์ _id ออกจากผลลัพธ์
        result.append(house)
    return result

@router.get("/getdetail")
async def get_house_detail(request: Request, house_id: str, db=Depends(get_database)):
    """
    ดึงข้อมูลบ้านตาม house_id และตรวจสอบสิทธิ์ด้วย access_token จาก HTTP-only cookies
    """
    token_data = verify_access_token_from_cookie(request)
    user_email = token_data["sub"]

    house = db["preProcessed_500"].find_one({"id": house_id})
    if not house:
        raise HTTPException(status_code=404, detail="House not found")

    del house['_id']  # ลบฟิลด์ _id ออกจากผลลัพธ์เพื่อหลีกเลี่ยงข้อผิดพลาด serialization
    return house
