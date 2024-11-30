from fastapi import APIRouter, HTTPException, Request
from app.utils.jwt_handler import verify_access_token_from_cookie
import httpx

router = APIRouter()

@router.post("/")
async def recommendation(request: Request, predict_method: str, asset_id: str):
    """
    รับ predict_method และ asset_id พร้อมตรวจสอบ access_token จาก HTTP-only cookies
    """
    token_data = verify_access_token_from_cookie(request)
    user_email = token_data["sub"]

    endpoints = {
        "collaborative_filtering": "http://localhost:8001/collaborative_filtering",
        "assoc_rules": "http://localhost:8001/assoc_rules",
        "hybrid": "http://localhost:8001/hybrid"
    }

    if predict_method not in endpoints:
        raise HTTPException(status_code=400, detail="Invalid prediction method")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                endpoints[predict_method],
                params={"latest_visited_asset_id": asset_id, "user_id": user_email}
            )
            response.raise_for_status()  # ตรวจสอบ HTTP status code
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Error from recommendation service: {exc.response.text}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    return response.json()
