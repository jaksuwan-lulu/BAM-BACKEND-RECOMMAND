from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from app.router import auth, user, house, recommendation
# กำหนด tokenUrl ให้ถูกต้อง
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

app = FastAPI()

# เพิ่ม Middleware CORS เพื่อรองรับการใช้งาน HTTP-only cookies
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,  
    allow_methods=["*"],  
    allow_headers=["*"]  
)

# รวม router ต่างๆ
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(house.router, prefix="/house", tags=["Houses"])
app.include_router(recommendation.router, prefix="/recommendation", tags=["Recommendations"])
# app.include_router(visited_pages.router, prefix="/visited_pages", tags=["Visited Pages"])

# สำหรับการรันเซิร์ฟเวอร์
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
    