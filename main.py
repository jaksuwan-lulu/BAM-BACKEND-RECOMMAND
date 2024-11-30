from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from app.router import auth, user, house, recommendation, visited_pages
from app.router.error_handler import http_error_handler, validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException

# กำหนด tokenUrl ให้ถูกต้อง
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

app = FastAPI()

# เพิ่ม Middleware CORS เพื่อรองรับการใช้งาน HTTP-only cookies
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # เปลี่ยน URL ให้ตรงกับ Frontend ของคุณ
    allow_credentials=True,  # เปิดใช้งาน cookies
    allow_methods=["*"],  # อนุญาตทุก HTTP methods (GET, POST, PUT, DELETE, ฯลฯ)
    allow_headers=["*"]  # อนุญาตทุก headers
)

# รวม router ต่างๆ
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(house.router, prefix="/house", tags=["Houses"])
app.include_router(recommendation.router, prefix="/recommendation", tags=["Recommendations"])
app.include_router(visited_pages.router, prefix="/visited_pages", tags=["Visited Pages"])

# เพิ่มตัวจัดการข้อผิดพลาด
app.add_exception_handler(HTTPException, http_error_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# สำหรับการรันเซิร์ฟเวอร์
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)