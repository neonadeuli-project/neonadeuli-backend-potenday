import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from app.error.chat_exception import ChatServiceException
from app.schemas.heritage import HeritageBuildingInfo, HeritageRouteInfo
from app.service.chat_service import ChatService


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def chat_service():
    mock_db = AsyncMock()

    # 비동기 컨텍스트 매니저를 모의하기 위한 클래스
    class AsyncContextManagerMock:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

    # begin 메서드가 AsyncContextManagerMock 인스턴스를 반환하도록 설정
    mock_db.begin = MagicMock(return_value=AsyncContextManagerMock())

    service = ChatService(mock_db)
    service.user_repository = AsyncMock()
    service.chat_repository = AsyncMock()
    service.heritage_repository = AsyncMock()
    service.validation_service = AsyncMock()
    service.clova_service = AsyncMock()
    service.s3_service = AsyncMock()
    return service


@pytest.mark.asyncio
async def test_create_chat_session_success(chat_service):
    # Arrange
    user_id = 1
    heritage_id = 100

    mock_session = MagicMock()
    mock_session.id = 1
    mock_session.start_time = datetime.now()
    mock_session.created_at = datetime.now()

    mock_heritage = MagicMock()
    mock_heritage.id = heritage_id
    mock_heritage.name = "Test Heritage"

    mock_routes = [
        HeritageRouteInfo(
            route_id=1,
            name="Test Route",
            buildings=[
                HeritageBuildingInfo(
                    building_id=1,
                    name="Test Building 1"
                ),
                HeritageBuildingInfo(
                    building_id=2,
                    name="Test Building 2", coordinate=(37.5, 127.0)
                ),
            ],
        )
    ]

    chat_service.chat_repository.create_chat_session = AsyncMock(
        return_value=mock_session
    )
    chat_service.heritage_repository.get_heritage_by_id = AsyncMock(
        return_value=mock_heritage
    )
    chat_service.heritage_repository.get_routes_with_buildings_by_heritages_id = (
        AsyncMock(return_value=mock_routes)
    )

    # Act
    try:
        result = await chat_service.create_chat_session(user_id, heritage_id)

        # Assert
        assert result.session_id == mock_session.id
        assert result.heritage_id == heritage_id
        assert result.heritage_name == "Test Heritage"
        assert len(result.routes) == len(mock_routes)

        for i, route in enumerate(result.routes):
            assert isinstance(route, HeritageRouteInfo)
            assert route.route_id == mock_routes[i].route_id
            assert route.name == mock_routes[i].name
            assert len(route.buildings) == len(mock_routes[i].buildings)

            for j, building in enumerate(route.buildings):
                assert isinstance(building, HeritageBuildingInfo)
                assert building.building_id == mock_routes[i].buildings[j].building_id
                assert building.name == mock_routes[i].buildings[j].name
                assert building.coordinate == mock_routes[i].buildings[j].coordinate

        # Verify that methods were called
        chat_service.chat_repository.create_chat_session.assert_awaited_once_with(
            user_id, heritage_id
        )
        chat_service.heritage_repository.get_heritage_by_id.assert_awaited_once_with(
            heritage_id
        )
        chat_service.heritage_repository.get_routes_with_buildings_by_heritages_id.assert_awaited_once_with(
            heritage_id
        )
    except ChatServiceException as e:
        pytest.fail(f"ChatService 예외 발생: {str(e)}")
    except Exception as e:
        pytest.fail(f"예상치 못한 예외 발생: {str(e)}")


@pytest.mark.asyncio
async def test_create_chat_session_database_error(chat_service):
    # Arrange
    user_id = 1
    heritage_id = 100
    chat_service.chat_repository.create_chat_session.side_effect = Exception(
        "DB 연결 에러"
    )

    # Act Assert
    with pytest.raises(ChatServiceException) as exc_info:
        await chat_service.create_chat_session(user_id, heritage_id)
    assert "채팅 세션 생성 실패" in str(exc_info.value)
