from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from app.router import auth, user, house, recommendation, visited_pages
from app.router.error_handler import http_error_handler, validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException

# กำหนด tokenUrl ให้ถูกต้อง
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

app = FastAPI()

# รวม router ต่างๆ พร้อมกำหนดการบังคับใช้ token ใน endpoint ที่ต้องการการรับรองความปลอดภัย
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/users", tags=["Users"], dependencies=[Depends(oauth2_scheme)])
app.include_router(house.router, prefix="/house", tags=["Houses and Favorites"])  # ไม่ต้องใช้ Depends สำหรับการเข้าถึงทั่วไป
app.include_router(recommendation.router, prefix="/recommendation", tags=["Recommendations"], dependencies=[Depends(oauth2_scheme)])
# app.include_router(visited_pages.router, prefix="/visited_page", tags=["Visited Pages"], dependencies=[Depends(oauth2_scheme)])
app.add_exception_handler(HTTPException, http_error_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
