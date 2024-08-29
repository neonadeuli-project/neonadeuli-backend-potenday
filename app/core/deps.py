from typing import Optional
from fastapi import HTTPException, Header, status
from app.core.database import AsyncSessionLocal

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
        await session.commit()
        # with을 사용하면 알아서 session을 닫아줌
        # await session.close()

async def get_token(Authorization: Optional[str] = Header(None)) -> str:
    if not Authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="인증 헤더 누락",
            headers={"WWW-Authenticate": "Bearer"}
        )
    try:
        scheme, token = Authorization.split()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 인증 헤더 포맷",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="유효하지 않은 인증 스키마",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰 누락",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return token