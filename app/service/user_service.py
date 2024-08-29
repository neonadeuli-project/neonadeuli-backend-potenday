import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi import Depends, HTTPException
from datetime import timedelta

from app.core.deps import get_db    
from app.error.auth_exception import (
    AuthServiceException, 
    DatabaseOperationException, 
    InvalidTokenException, 
    UserCreationException, 
    UserNotFoundException
)
from app.repository.user_repository import UserRepository
from app.models.user import User
from app.core.security import create_access_token 

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)

    # 헤더 Token 기반 임시 유저 생성
    async def create_temp_user(self, username: str) -> User:
            try:
                user = await self.user_repository.create_temp_user(name=username, token=None)

                if not user:
                    raise UserCreationException("사용자 생성 실패")

                access_token = create_access_token(
                    data={"sub": str(user.id)},
                    expires_delta=timedelta(hours=1)
                )
                
                updated_user = await self.user_repository.update_user_token(user.id, access_token)
                
                if not updated_user:
                    raise UserCreationException("사용자 토큰 업데이트 실패")
                
                return updated_user
            except SQLAlchemyError as e:
                logger.error(f"임시 유저 생성 중 데이터베이스 오류 발생: {str(e)}")
                raise UserCreationException(f"데이터베이스 오류: {str(e)}")
            except Exception as e:
                logger.error(f"임시 유저 생성 중 예상치 못한 오류 발생: {str(e)}")
                raise UserCreationException(str(e))
    
    async def get_user_by_token(self, token: str) -> User:
        try:
            user = await self.user_repository.get_user_by_token(token)
            if not user:
                raise UserNotFoundException(f"토큰: {token}")
            return user
        except UserNotFoundException as e:
            raise InvalidTokenException()
        except DatabaseOperationException as e:
            logger.error(f"데이터베이스 오류 발생: {str(e)}")
            raise AuthServiceException("서비스 일시적 오류")
        except Exception as e:
            logger.error(f"토큰 검증 중 예상치 못한 오류 발생: {str(e)}")
            raise AuthServiceException("토큰 검증 중 오류 발생")
    
    # 유저 토큰 삭제
    async def invalidate_token(self, token: str) -> bool:
        try:
            user = await self.user_repository.get_user_by_token(token)
            if not user:
                raise InvalidTokenException(token)
            
            success = await self.user_repository.update_user_token(user.id, None)
            if not success:
                raise DatabaseOperationException("토큰 업데이트 실패")
            
            return True
        except InvalidTokenException as e:
            logger.warning(f"유효하지 않은 토큰: {str(e)}")
            raise
        except DatabaseOperationException as e:
            logger.error(f"데이터베이스 오류: {str(e)}")
            raise AuthServiceException("서비스 일시적 오류")
        except Exception as e:
            logger.error(f"토큰 무효화 오류 발생: {str(e)}")
            raise AuthServiceException("토큰 무효화 중 오류 발생")