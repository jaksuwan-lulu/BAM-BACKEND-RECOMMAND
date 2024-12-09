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
    query: Optional[str] = None,
    provice: Optional[str] = None,
    asset_type: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    db=Depends(get_database)
):
    """
    ค้นหาบ้านตามเงื่อนไขที่กำหนด เช่น asset_id, asset_project_name, asset_type, no_of_rights_document,
    address, provice, district, และ sub_district
    """

    search_conditions = {}


    or_conditions = []
    if query:
        or_conditions.extend([
            {"asset_id": {"$regex": query, "$options": "i"}}, 
            {"asset_project_name": {"$regex": query, "$options": "i"}},
            {"asset_type": {"$regex": query, "$options": "i"}},
            {"no_of_rights_document": {"$regex": query, "$options": "i"}}, 
            {"address": {"$regex": query, "$options": "i"}},
            {"provice": {"$regex": provice, "$options": "i"}},
            {"district": {"$regex": query, "$options": "i"}},
            {"sub_district": {"$regex": query, "$options": "i"}}
        ])
    if or_conditions:
        search_conditions["$or"] = or_conditions

    if provice:
        search_conditions["provice"] = {"$regex": provice, "$options": "i"}
    if asset_type:
        search_conditions["asset_type"] = {"$regex": asset_type, "$options": "i"}


    houses_cursor = db["preProcessed_500"].find(search_conditions)


    houses = []
    for house in houses_cursor:
        try:

            price = int(house.get("price", "").replace(" บาท", "").replace(",", "").strip())
            house["price"] = price
        except (ValueError, AttributeError):

            continue


        if min_price is not None and price < min_price:
            continue
        if max_price is not None and price > max_price:
            continue


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
