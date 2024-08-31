from typing import Any, Dict
from app.error.chat_exception import SessionNotFoundException
from app.repository.chat_repository import ChatRepository
from app.repository.heritage_repository import HeritageRepository
from app.error.heritage_exceptions import (
    BuildingNotFoundException,
    InvalidAssociationException,
)
from sqlalchemy.ext.asyncio import AsyncSession


class ValidationService:
    def __init__(self, db: AsyncSession):
        self.chat_repository = ChatRepository(db)
        self.heritage_repository = HeritageRepository(db)

    async def validate_session_and_building(
        self, session_id: int, building_id: int
    ):
        chat_session = await self.chat_repository.get_chat_session(session_id)
        if not chat_session:
            raise SessionNotFoundException(session_id)

        building = await self.heritage_repository.get_heritage_building_by_id(
            building_id
        )
        if not building:
            raise BuildingNotFoundException(building_id)

        if building.heritage_id != chat_session.heritage_id:
            raise InvalidAssociationException(session_id, building_id)

        return chat_session, building

    async def is_valid_quiz(self, parsed_quiz: Dict[str, Any]) -> bool:
        return (
            parsed_quiz["question"]
            and len(parsed_quiz["options"]) >= 2
            and parsed_quiz["answer"]
            and parsed_quiz["answer"].isdigit()
            and parsed_quiz["explanation"]
        )
