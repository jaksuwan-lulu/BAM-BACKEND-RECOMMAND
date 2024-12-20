from fastapi import APIRouter, Depends, HTTPException, Request
from app.database.database import get_database
from app.models.models import FavoriteHouses
import logging
from typing import Optional

router = APIRouter()

db = get_database()  

@router.get("/")
async def get_houses(db=Depends(get_database)):
    """
    ดึงข้อมูลบ้านทั้งหมดจาก collection preProcessed_500
    """
    houses_cursor = db["preProcessed_500"].find()
    houses = []
    for house in houses_cursor:
        del house['_id']  
        houses.append(house)
    return houses

@router.get("/search")
async def search_houses(
    asset_project_name: Optional[str] = None,
    asset_type: Optional[str] = None,
    district: Optional[str] = None,
    provice: Optional[str] = None,
    sub_district: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    db=Depends(get_database)
):
    """
    ค้นหาบ้านตามเงื่อนไขที่กำหนด เช่น asset_project_name, asset_type, district, provice, และ sub_district
    โดยแสดงเฉพาะข้อมูลที่ขึ้นต้นด้วยค่าที่กำหนด
    """

    # เงื่อนไขการค้นหา
    search_conditions = {}

    if asset_project_name:
        search_conditions["asset_project_name"] = {"$regex": f"^{asset_project_name}", "$options": "i"}
    if asset_type:
        search_conditions["asset_type"] = {"$regex": f"^{asset_type}", "$options": "i"}
    if district:
        search_conditions["district"] = {"$regex": f"^{district}", "$options": "i"}
    if provice:
        search_conditions["provice"] = {"$regex": f"^{provice}", "$options": "i"}
    if sub_district:
        search_conditions["sub_district"] = {"$regex": f"^{sub_district}", "$options": "i"}

    # ใช้ projection เพื่อดึงเฉพาะฟิลด์ที่ต้องการ
    projection = {
        "asset_id": 1,  # เพิ่ม asset_id
        "asset_project_name": 1,
        "asset_type": 1,
        "district": 1,
        "provice": 1,
        "sub_district": 1,
        "price": 1
    }

    # ค้นหาเอกสารใน MongoDB
    houses_cursor = db["preProcessed_500"].find(search_conditions, projection)

    houses = []
    for house in houses_cursor:
        try:
            # แปลง price เป็น integer
            price = int(house.get("price", "").replace(" บาท", "").replace(",", "").strip())
            house["price"] = price
        except (ValueError, AttributeError):
            continue

        # กรองตามราคา
        if min_price is not None and price < min_price:
            continue
        if max_price is not None and price > max_price:
            continue

        # ลบ `_id` ออก
        house.pop("_id", None)
        houses.append(house)

    if not houses:
        raise HTTPException(status_code=404, detail="ไม่พบผลลัพธ์")

    return {"results": houses}







@router.get("/getdetail")
async def get_house_detail(asset_id: str, db=Depends(get_database)):
    logging.info(f"Received request with asset_id: {asset_id}")

    try:

        house = db["preProcessed_500"].find_one({"asset_id": asset_id})
        logging.info(f"Query result: {house}")
    except Exception as e:
        logging.error(f"Database query failed: {e}")
        raise HTTPException(status_code=500, detail="Database query failed")


    if not house:
        logging.warning(f"No document found with asset_id: {asset_id}")
        raise HTTPException(status_code=404, detail="House not found")

    if "_id" in house:
        del house["_id"]

    logging.info(f"Returning house details: {house}")
    return house
