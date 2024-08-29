import logging
import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_token    
from app.core.security import decode_token
from app.error.auth_exception import (
    AuthServiceException,
    InvalidTokenException,
    UserCreationException
)
from app.schemas.user import UserValidationResponse, UserTempLoginResponse, UserLogoutResponse
from app.service.user_service import UserService

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 임시 로그인
@router.post("/login", response_model=UserTempLoginResponse)
async def temp_login(db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    
    # 랜덤 닉네임 생성
    random_username = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    
    try:
        # 임시 유저 생성
        user = await user_service.create_temp_user(random_username)
        
        return UserTempLoginResponse (
            id=user.id,
            username=user.name,
            access_token=user.token,
            token_type="bearer"
        )
    except UserCreationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AuthServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="서버 내부 에러")

# 토큰 검증
@router.get("/validate_token", response_model=UserValidationResponse)
async def validate_token(token: str = Depends(get_token), db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    try:
        user = await user_service.get_user_by_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="사용자를 찾을 수 없습니다.",
                hearders={"WWW-Authenticate": "Bearer"}
            )

        return UserValidationResponse(
            id=user.id,
            username=user.name,
            created_at=user.created_at
        )
    except InvalidTokenException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰")
    except Exception as e:
        logger.error(f"토큰 유효성 검사 중 예상치 못한 에러: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="서버 내부 에러")



#로그아웃
@router.post("/logout", response_model=UserLogoutResponse)
async def logout(token: str = Depends(get_token), db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    try:
        success = await user_service.invalidate_token(token)
        if success:
            return UserLogoutResponse(message="로그아웃 성공",success=True)
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="로그아웃 실패")
    except InvalidTokenException as e:
        logger.warning(f"로그아웃 시도 중 유효하지 않은 토큰: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e), headers={"WWW-Authenticate" : "Bearer"})
    except AuthServiceException as e:
        logger.error(f"로그아웃 중 서비스 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        logger.error(f"로그아웃 중 예상치 못한 오류 발생: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="서버 내부 에러")