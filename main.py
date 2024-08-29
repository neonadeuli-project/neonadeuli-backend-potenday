from fastapi import FastAPI
from fastapi.routing import APIRoute

from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.models.init import (
    User, 
    Heritage, 
    ChatSession, 
    ChatMessage,
    HeritageBuilding,
    HeritageBuildingImage,
    HeritageRoute,
    HeritageRouteBuilding,
    HeritageType
)
from app.core.database import Base, engine
from app.core.config import settings
from app.router.api import api_router
from contextlib import asynccontextmanager

def custom_generate_unique_id(route: APIRoute) -> str:
    if route.tags:
        return f"{route.tags[0]}-{route.name}"
    return route.name

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # 애플리케이션 시작 시 실행될 로직
    async with engine.begin() as conn:
        # 모든 테이블 삭제
        # await conn.run_sync(Base.metadata.drop_all)
        # 모든 테이블 다시 생성
        await conn.run_sync(Base.metadata.create_all)
    yield
    # 애플리케이션 종료 시 실행될 로직 (필요한 경우)

app = FastAPI(
    lifespan= app_lifespan,
    # 배포 시 swagger UI, Redoc 비활성화
    # docs_url= None,
    # redoc_url= None,
    title = settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id
)

app.add_middleware(SessionMiddleware, secret_key=settings.BACKEND_SESSION_SECRET_KEY)
# Base.metadata.create_all(bind=engine)

# Set All CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
