from flask import app
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.deps import get_db
from app.core.database import Base
from app.models.chat.chat_session import ChatSession

# 테스트용 데이터베이스 URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture
async def test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def client(test_db):
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.mark.asyncio
async def test_end_chat_session(client):
    # 테스트 데이터 준비
    session_id = 1
    visited_buildings = {
        "buildings": [
            {"name": "광화문", "visited": True},
            {"name": "근정전", "visited": True},
            {"name": "경회루", "visited": False}
        ]
    }

    # API 호출
    response = client.post(f"/sessions/{session_id}/end", json=visited_buildings)
    
    # 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "end_time" in data

@pytest.mark.asyncio
async def test_get_chat_summary(client):
    # 테스트 데이터 준비
    session_id = 1

    # 요약 정보가 없는 경우 테스트
    response = client.get(f"/sessions/{session_id}/summary")
    assert response.status_code == 404

    # 요약 정보 생성 (실제 환경에서는 비동기로 생성되지만, 테스트에서는 직접 생성)
    # 여기서는 예시로 직접 데이터를 삽입하는 방식을 사용합니다.
    async with TestingSessionLocal() as session:
        chat_session = ChatSession(
            id=session_id,
            summary_keywords=["경복궁", "조선시대", "광화문"],
            visited_buildings=[{"name": "광화문", "visited": True}, {"name": "근정전", "visited": True}],
            summary_generated="2024-08-01T12:00:00"
        )
        session.add(chat_session)
        await session.commit()

    # 요약 정보 조회 테스트
    response = client.get(f"/sessions/{session_id}/summary")
    assert response.status_code == 200
    data = response.json()
    assert "chat_date" in data
    assert "heritage_name" in data
    assert "building_course" in data
    assert "keywords" in data

# 추가 테스트 케이스들...