from fastapi import APIRouter

from app.router.v1 import user, chat, image, heritage

api_router = APIRouter()

api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(
    heritage.router, prefix="/heritages", tags=["heritages"]
)
api_router.include_router(image.router, prefix="/image", tags=["image"])
