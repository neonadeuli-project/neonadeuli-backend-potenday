from fastapi import APIRouter

from app.router.v1 import chat, heritage, image, user

api_router = APIRouter()


@api_router.get("/health")
def health_check():
    return {"status": "ok"}


api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(heritage.router, prefix="/heritages", tags=["heritages"])
api_router.include_router(image.router, prefix="/image", tags=["image"])
