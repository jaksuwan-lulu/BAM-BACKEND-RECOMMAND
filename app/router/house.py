from fastapi import APIRouter, Depends, HTTPException
from pymongo import MongoClient
from app.utils.jwt_handler import verify_access_token
from app.database.database import get_database
from app.models.models import FavoriteHouses
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

router = APIRouter()
client = MongoClient("mongodb://localhost:27017/")
db = client['bamAssetsRecommendation']

# ดึงข้อมูลจากคอลเล็กชัน preProcessed_500
@router.get("/")
async def get_houses(db=Depends(get_database)):
    houses_cursor = db["preProcessed_500"].find()
    houses = []
    for house in houses_cursor:
        del house['_id']
        houses.append(house)
    return houses

@router.get("/search")
async def search_houses(query: str, db=Depends(get_database)):
    houses = db['preProcessed_500'].find({"asset_project_name": {"$regex": query, "$options": "i"}})
    
    result = []
    for house in houses:
        del house['_id']
        result.append(house)
    return result

# Endpoint นี้ต้องการ authentication และจะมีแม่กุญแจใน Swagger UI

# @router.post("/add-favorite")
# async def toggle_favorite(asset_id: str, token: str = Depends(oauth2_scheme)):
#     db = get_database()  # เรียกใช้ฐานข้อมูลภายในฟังก์ชัน
#     token_data = verify_access_token(token)  # ส่งแค่ token อย่างเดียว

#     if not token_data:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")

#     user_email = token_data['sub']  # ดึงค่า email จาก token

#     # ตรวจสอบว่า asset_id มีอยู่ใน collection 'preProcessed_500' หรือไม่
#     asset = db['preProcessed_500'].find_one({"asset_id": asset_id})
#     if not asset:
#         raise HTTPException(status_code=404, detail="Asset not found")

#     # ตรวจสอบว่ารายการนี้มีอยู่แล้วใน collection 'favorite'
#     existing_favorite = db['favorite'].find_one({"email": user_email, "asset_id": asset_id})
    
#     if existing_favorite:
#         # ถ้ามีอยู่แล้ว ให้ลบรายการออก
#         db['favorite'].delete_one({"email": user_email, "asset_id": asset_id})
#         return {"message": "House removed from favorite list"}
#     else:
#         # ถ้าไม่มี ให้เพิ่มรายการใหม่
#         favorite = {
#             "email": user_email,
#             "asset_id": asset_id
#         }
#         db['favorite'].insert_one(favorite)
#         return {"message": "House added to favorite list"}



