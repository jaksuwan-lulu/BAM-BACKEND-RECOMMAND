from fastapi import APIRouter, Depends, HTTPException
from app.database.database import get_database
from app.utils.jwt_handler import verify_access_token
from datetime import datetime
import random
from app.models.models import User  # เรียกใช้จาก model.py

router = APIRouter()

@router.post("/visit")
async def simulate_visit(token: str = Depends(verify_access_token), db=Depends(get_database)):
    user_email = token["sub"]
    user = await db["users"].find_one({"users_email": user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    random_ids = random.sample(range(1, 101), 5)
    visited_pages = [{"users_email": user_email, "id": house_id, "timestamp": datetime.utcnow()} for house_id in random_ids]

    await db["visited_pages"].insert_many(visited_pages)
    return {"message": "Page visits recorded successfully", "visited_ids": random_ids}
