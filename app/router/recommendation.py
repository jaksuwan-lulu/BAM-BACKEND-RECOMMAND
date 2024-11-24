from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter()

@router.post("/")
async def recommendation(predict_method: str, asset_id: str):
    endpoints = {
        'collaborative_filtering': 'http://localhost:8001/collaborative_filtering',
        'assoc_rules': 'http://localhost:8001/assoc_rules',  # ตรวจสอบให้แน่ใจว่า path นี้ถูกต้อง
        'hybrid': 'http://localhost:8001/hybrid'
    }

    if predict_method not in endpoints:
        raise HTTPException(status_code=400, detail="Invalid prediction method")

    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(
                endpoints[predict_method],
                params={'latest_visited_asset_id': asset_id, 'user_id': 'example@example.com'}
            )
            res.raise_for_status()  # เพิ่มการตรวจสอบสถานะ HTTP
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=f"Error from recommendation service: {exc.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    return res.json()
