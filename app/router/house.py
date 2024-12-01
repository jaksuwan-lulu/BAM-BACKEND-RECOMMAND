from fastapi import APIRouter, Depends, HTTPException, Request
from app.utils.jwt_handler import verify_access_token_from_cookie
from app.database.database import get_database
from app.models.models import FavoriteHouses
import logging

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
async def get_house_detail(asset_id: str, db=Depends(get_database)):
    logging.info(f"Received request with asset_id: {asset_id}")

    try:
        # Query จาก MongoDB
        house = db["preProcessed_500"].find_one({"asset_id": asset_id})
        logging.info(f"Query result: {house}")
    except Exception as e:
        logging.error(f"Database query failed: {e}")
        raise HTTPException(status_code=500, detail="Database query failed")

    # กรณีไม่พบบ้าน
    if not house:
        logging.warning(f"No document found with asset_id: {asset_id}")
        raise HTTPException(status_code=404, detail="House not found")

    # ลบ `_id` ก่อนส่งกลับ
    if "_id" in house:
        del house["_id"]

    logging.info(f"Returning house details: {house}")
    return house

