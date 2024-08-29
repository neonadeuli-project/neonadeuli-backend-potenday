import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.error.chat_exception import (
    ChatServiceException, 
    NoQuizAvailableException, 
    QuizGenerationException,
    SessionNotFoundException, 
    SummaryNotFoundException
)
from app.service.chat_service import ChatService
from app.schemas.heritage import (
    BuildingInfoButtonResponse,
    BuildingInfoButtonRequest,
    BuildingQuizButtonResponse,
    BuildingQuizButtonRequest,
    RecommendedQuestionRequest,
    RecommendedQuestionResponse
)    
from app.schemas.chat import (
    ChatSessionCreateResponse, 
    ChatSessionCreateRequest, 
    ChatMessageRequest,
    ChatMessageResponse, 
    ChatSessionEndResponse,
    ChatSessionStatusResponse,
    ChatSummaryResponse,
    VisitedBuildingList
)
from app.error.heritage_exceptions import (
    BuildingNotFoundException, 
    InvalidAssociationException
)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 새로운 채팅 세션 생성
@router.post("/sessions", response_model=ChatSessionCreateResponse)
async def create_chat_session(
    chat_session: ChatSessionCreateRequest, 
    db: AsyncSession = Depends(get_db)
):
    chat_service = ChatService(db)
    try:
        return await chat_service.create_chat_session(chat_session.user_id, chat_session.heritage_id)
    
    except ChatServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"채팅 세션 생성 중 예상치 못한 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="서버에 오류가 발생했습니다.")


# 채팅 메시지 전송
@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def add_chat_message(
    session_id: int,
    message: ChatMessageRequest,
    background_tasks: BackgroundTasks, 
    db: AsyncSession = Depends(get_db)
):
    chat_service = ChatService(db)
    try:
        return await chat_service.update_chat_conversation(session_id, message.content)
       
    except SessionNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ChatServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"메시지 전송 중 예상치 못한 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="서버 오류가 발생했습니다.")

# 건축물 정보 제공
@router.post("/{session_id}/heritage/buildings/info", response_model=BuildingInfoButtonResponse)
async def get_heritage_building_info(
    session_id: int,
    building_data: BuildingInfoButtonRequest,
    db: AsyncSession = Depends(get_db)
):
    chat_service = ChatService(db)
    try:
        return await chat_service.update_info_conversation(session_id, building_data.building_id)
        
    except (SessionNotFoundException, BuildingNotFoundException, InvalidAssociationException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ChatServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"건축물 정보 제공 중 예상치 못한 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="서버 오류가 발생했습니다.")

# 건축물 퀴즈 제공
@router.post("/{session_id}/heritage/buildings/quiz", response_model=BuildingQuizButtonResponse)
async def get_heritage_building_quiz(
    session_id: int,
    building_data: BuildingQuizButtonRequest,
    db: AsyncSession = Depends(get_db)
):
    chat_service = ChatService(db)
    try:
        return await chat_service.update_quiz_conversation(session_id, building_data.building_id)

    except (SessionNotFoundException, BuildingNotFoundException, InvalidAssociationException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NoQuizAvailableException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except QuizGenerationException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ChatServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"퀴즈 제공 중 예상치 못한 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="서버 오류가 발생했습니다.")
    
# 건축물 추천 질문 제공
@router.post("/{session_id}/building/recommend-questions", response_model=RecommendedQuestionResponse)
async def get_building_recommented_questions(
    session_id: int,
    building_data: RecommendedQuestionRequest,
    db: AsyncSession = Depends(get_db)
):
    chat_service = ChatService(db)
    try:
        return await chat_service.get_building_questions(session_id, building_data.building_id)
    
    except (SessionNotFoundException, BuildingNotFoundException, InvalidAssociationException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"퀴즈 제공 중 예상치 못한 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="서버 오류가 발생했습니다.")
    
# 메시지 추천 질문 제공
@router.get("/{session_id}/message/recommend-questions", response_model=List[str])
async def get_message_recommented_questions(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    chat_service = ChatService(db)
    try:
        return await chat_service.get_message_questions(session_id)
    
    except (SessionNotFoundException, BuildingNotFoundException, InvalidAssociationException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"퀴즈 제공 중 예상치 못한 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="서버 오류가 발생했습니다.")
    
    
# 채팅 요약 제공
@router.get("/sessions/{session_id}/summary", response_model=ChatSummaryResponse)
async def get_chat_summary(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    chat_service = ChatService(db)
    try:    
        return await chat_service.update_summary_conversation(session_id)
    
    except SummaryNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ChatServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"퀴즈 제공 중 예상치 못한 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="서버 오류가 발생했습니다.")

# 채팅 세션 종료
@router.post("/sessions/{session_id}/end", response_model=ChatSessionEndResponse)
async def end_chat_session(
    session_id: int,
    visited_buildings: VisitedBuildingList,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    chat_service = ChatService(db)
    try:
        # 요약 작업 백그라운드 실행
        background_tasks.add_task(
            chat_service.generated_and_save_chat_summary,
            session_id,
            visited_buildings.buildings
        )

        return await chat_service.end_chat_session(session_id)
    
    except SessionNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ChatServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"퀴즈 제공 중 예상치 못한 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="서버 오류가 발생했습니다.")
    
# 채팅 세션 종료 여부 확인
@router.get("/sessions/{session_id}/status", response_model=ChatSessionStatusResponse)
async def check_chat_session_status(session_id: int, db: AsyncSession = Depends(get_db)):
    chat_service = ChatService(db)
    try:
        ended_status = await chat_service.is_chat_session_ended(session_id)
        return ChatSessionStatusResponse(
            session_id=session_id,
            ended_status=ended_status
        )
    except SessionNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ChatServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"퀴즈 제공 중 예상치 못한 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="서버 오류가 발생했습니다.")