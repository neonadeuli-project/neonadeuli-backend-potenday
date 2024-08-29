import logging
from typing import List, Optional
from datetime import datetime

from fastapi import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, values, desc, delete
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func
from sqlalchemy.orm import joinedload

from app.error.auth_exception import DatabaseOperationException, UserNotFoundException
from app.error.chat_exception import ChatServiceException, SessionNotFoundException
from app.error.heritage_exceptions import HeritageNotFoundException
from app.models.chat.chat_session import ChatSession
from app.models.chat.chat_message import ChatMessage
from app.models.enums import RoleType
from app.models.question import RecommendedQuestion
from app.models.user import User
from app.models.heritage.heritage import Heritage
from app.schemas.chat import VisitedBuilding

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.config import settings

logger = logging.getLogger(__name__)

# Create a new async engine and session factory
engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

class ChatRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # 채팅 세션 생성
    async def create_chat_session(self, user_id: int, heritage_id: int) -> ChatSession:
        logger.info(f"ChatRepository에서 채팅 세션을 생성합니다. (user_id: {user_id}, heritage_id: {heritage_id})")
        try:
            # 채팅 세션 활성화 상태 확인
            active_session = await self.get_active_session(user_id, heritage_id)
            if active_session:
                logger.info(f"기존 활성 세션을 반환합니다. (session_id: {active_session.id})")
                return active_session

            # 사용자 여부 확인 & 새 세션 생성
            user = await self.db.execute(select(User).where(User.id == user_id))
            user = user.scalar_one_or_none()
            if not user:
                raise UserNotFoundException(f"등록되지 않은 사용자입니다. (user_id: {user.id})")
            
            # 문화재 여부 확인
            heritage = await self.db.execute(select(Heritage).where(Heritage.id == heritage_id))
            heritage = heritage.scalar_one_or_none()
            if not heritage:
                raise HeritageNotFoundException(f"등록되지 않은 문화재입니다. (heritage_id: {heritage_id})")
            
            # 채팅 세션 생성
            new_session = ChatSession(
                user_id=user_id, 
                heritage_id=heritage_id,
                heritage_name=heritage.name,
                start_time=datetime.now(),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.db.add(new_session)
            await self.db.flush()
            await self.db.refresh(new_session)
            
            logger.info(f"새로운 채팅 세션이 생성되었습니다. (session_id: {new_session.id}, user_id: {user_id}, heritage_id: {heritage_id})")
            
            return new_session

        except (UserNotFoundException, HeritageNotFoundException) as e:
            logger.error(f"채팅 세션 생성 중 에러 발생: {str(e)}", exc_info=True)
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error in create_chat_session: {str(e)}", exc_info=True)
            raise DatabaseOperationException("채팅 세션 생성 중 데이터베이스 오류 발생")
        except Exception as e:
            logger.error(f"Unexpected error in create_chat_session: {str(e)}", exc_info=True)
            raise ChatServiceException("채팅 세션 생성 중 예상치 못한 오류 발생")

    # 채팅 세션 활성화 상태 조회
    async def get_active_session(self, user_id: int, heritage_id: int) -> Optional[ChatSession]:
        try:
            result = await self.db.execute(select(ChatSession)
                                        .where(
                                            (ChatSession.user_id == user_id) &
                                            (ChatSession.heritage_id == heritage_id) &
                                            (ChatSession.end_time == None) # 세션 종료 유무 확인
                                        )
                                        .order_by(ChatSession.created_at.desc())
                                        )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"채팅 활성화 상태 조회 중 데이터베이스 오류 발생 : {str(e)}", exc_info=True)
            raise DatabaseOperationException("활성 세션 조회 중 데이터베이스 오류 발생")
    
    # 채팅 세션 종료
    async def end_chat_session(self, session_id: int) -> Optional[ChatSession]:
        try:
            await self.db.execute(update(ChatSession)
                                            .where(
                                                (ChatSession.id == session_id) &
                                                (ChatSession.end_time == None)
                                            )
                                            .values(end_time=func.now())
                                        )
            await self.db.commit()

            # 업데이트 된 세션 조회
            result = await self.db.execute(select(ChatSession)
                                           .where(ChatSession.id == session_id)
                                        )
            updated_session = result.scalar_one_or_none()

            if updated_session:
                logger.info(f"채팅 세션 ID {session_id} 가 성공적으로 종료되었습니다.")
                # 세션 객체 반환을 위해 필요한 관계들을 로드
                # await self.db.refresh(updated_session, ['users', 'heritages', 'chat_messages'])
            else:
                logger.info(f"종료할 채팅 세션 ID가 {session_id} 인 활성 세션을 찾을 수 없습니다.")
                raise SessionNotFoundException(f"세션 ID {session_id}인 채팅 세션을 찾을 수 없습니다.")
            
            return updated_session
            
        except SQLAlchemyError as e:
            logger.error(f"채팅 세션 ID가 {session_id} 인 채팅 세션이 종료되는 동안 데이터 베이스에 오류가 발생했습니다.: {str(e)}")
            await self.db.rollback()
            raise DatabaseOperationException(f"데이터베이스 오류 : {str(e)}")
        except SessionNotFoundException:
            raise
        except Exception as e:
            logger.error(f"채팅 세션 ID가 {session_id} 인 채팅 세션이 종료되는 동안 예상치 못한 에러 발생 : {str(e)}")
            await self.db.rollback()
            raise ChatServiceException(f"예상치 못한 오류 : {str(e)}")
    
    # 새로운 채팅 메시지 저장 (새 레코드 추가)
    async def create_message(self, session_id: int, role: RoleType, content: str) -> ChatMessage:
        try:
            new_message = ChatMessage(
                session_id=session_id,
                role=role.value,
                content=content,
                timestamp=datetime.now()
            )
            self.db.add(new_message)
            await self.db.flush()
            await self.db.refresh(new_message)
            return new_message
        except SQLAlchemyError as e:
            logger.error(f"메시지 생성 중 데이터베이스 오류 발생: {str(e)}", exc_info=True)
            raise DatabaseOperationException("메시지 생성 중 데이터베이스 오류 발생")
    
    # 기존 채팅 메시지 업데이트 (특정 레코드 수정)
    async def update_message(self, session_id: int, **kwargs):
        try:
            await self.db.execute(
                update(ChatSession).
                where(ChatSession.id == session_id).
                values(**kwargs)
            )
            await self.db.commit()
        except SQLAlchemyError as e:
            logger.error(f"메시지 업데이트 중 데이터베이스 오류 발생: {str(e)}", exc_info=True)
            await self.db.rollback()
            raise DatabaseOperationException("메시지 업데이트 중 데이터베이스 오류 발생")
    
    # 채팅 최근 저장된 메시지 1개 조회
    async def get_latest_message(self, session_id: int, role: RoleType) -> Optional[ChatMessage]:
        try:
            result = await self.db.execute(select(ChatMessage)
                                           .where((ChatMessage.session_id == session_id) & (ChatMessage.role == role.value)
                                        ).order_by(desc(ChatMessage.timestamp)).limit(1))
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"최근 메시지 조회 중 데이터베이스 오류 발생: {str(e)}", exc_info=True)
            await self.db.rollback()
            raise DatabaseOperationException("최근 메시지 조회 중 데이터베이스 오류 발생") 
    
    # 특정 채팅 세션 조회
    async def get_chat_session(self, session_id: int) -> Optional[ChatSession]:
        try:
            result = await self.db.execute(select(ChatSession)
                                        .where(ChatSession.id == session_id))
            return result.scalar_one_or_none()
        except SessionNotFoundException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"채팅 세션 조회 중 데이터베이스 오류 발생: {str(e)}", exc_info=True)
            raise DatabaseOperationException("채팅 세션 조회 중 데이터베이스 오류 발생")
        
    # 추천 질문 조회
    async def get_recommended_questions(self, session_id: int) -> List[str]:
        try:
            result = await self.db.execute(select(RecommendedQuestion)
                                           .where(RecommendedQuestion.session_id == session_id)
                                           .order_by(RecommendedQuestion.id)
                                        )
            questions = result.scalars().all()
            
            # 문자열 리스트로 전환
            question_texts = [question.question for question in questions]
            return question_texts
        except Exception as e:
            logger.error(f"메시지 추천 질문 조회 중 오류 발생 : {str(e)}", exc_info=True)
            raise

    # 추천 질문 저장
    async def save_recommended_questions(self, session_id: int, questions: List[str]):
        async with SessionLocal() as session:
            async with session.begin():
                try:
                    # 기존 추천 질문이 있다면 삭제
                    await session.execute(delete(RecommendedQuestion)
                                        .where(RecommendedQuestion.session_id == session_id)
                                        )
                    # 새로운 추천 질문 저장
                    for question in questions:
                        new_question = RecommendedQuestion(session_id=session_id, question=question)
                        session.add(new_question)

                    await session.commit()

                except Exception as e:
                    await session.rollback()
                    logger.error(f"메시지 추천 질문 저장 중 오류 발생: {str(e)}", exc_info=True)
                    raise
    
    # 채팅 요약 정보 조회
    async def get_chat_summary(self, session_id: int):
        try:
            result = await self.db.execute(select(ChatSession)
                                        .options(joinedload(ChatSession.heritages))
                                        .where(ChatSession.id == session_id)
                                    )
            chat_session = result.scalar_one_or_none()

            if chat_session and chat_session.summary_keywords and chat_session.visited_buildings:
                return {
                    "chat_date": chat_session.start_time,
                    "heritage_name": chat_session.heritages.name,
                    "building_course": chat_session.visited_buildings,
                    "keywords": chat_session.summary_keywords
                }
            
            return None
        except SQLAlchemyError as e:
            logger.error(f"채팅 요약 조회 중 데이터베이스 오류 발생: {str(e)}", exc_info=True)
            raise DatabaseOperationException("채팅 요약 조회 중 데이터베이스 오류 발생")
    
    # 채팅 요약 정보 저장
    async def save_chat_summary(self, session_id: int, keywords: List[str], visited_buildings: List[VisitedBuilding]):
        try:
            await self.db.execute(update(ChatSession)
                                .where(ChatSession.id == session_id)
                                .values(
                                    summary_keywords=keywords,
                                    visited_buildings=[building.model_dump() for building in visited_buildings],
                                    summary_generated_at=func.now()
                                    )
                                )
            await self.db.commit()
        except SQLAlchemyError as e:
            logger.error(f"채팅 요약 저장 중 데이터베이스 오류 발생: {str(e)}", exc_info=True)
            await self.db.rollback()
            raise DatabaseOperationException("채팅 요약 저장 중 데이터베이스 오류 발생")