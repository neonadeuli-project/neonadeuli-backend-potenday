from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.schemas.heritage import HeritageBuildingInfo, HeritageRouteInfo


# 새로운 채팅 세션 생성 요청 값
class ChatSessionCreateRequest(BaseModel):
    user_id: int
    heritage_id: int


# 새로운 채팅 세션 생성 응답 값
class ChatSessionCreateResponse(BaseModel):
    session_id: int
    start_time: datetime
    created_at: datetime
    heritage_id: int
    heritage_name: str
    routes: List[HeritageRouteInfo]


# 채팅 메시지 생성 요청 값
class ChatMessageRequest(BaseModel):
    content: str
    role: Optional[str] = None
    timestamp: Optional[datetime] = None


# 채팅 메시지 응답 값
class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    timestamp: datetime
    # audio_url: Optional[str] = None


# 채팅 세션 종료 응답 값
class ChatSessionEndResponse(BaseModel):
    session_id: int
    end_time: datetime


# 채팅 세션 종료 상태 응답 값
class ChatSessionStatusResponse(BaseModel):
    session_id: int
    ended_status: bool


# 채팅 요약에 사용자 방문 코스 요청 값
class VisitedBuilding(BaseModel):
    name: str
    visited: bool


class VisitedBuildingList(BaseModel):
    buildings: List[VisitedBuilding]


# 채팅 요약 응답 값
class ChatSummaryResponse(BaseModel):
    chat_date: datetime
    heritage_name: str
    building_course: List[str]
    keywords: List[str]
