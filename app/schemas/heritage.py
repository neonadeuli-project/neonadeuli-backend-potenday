from typing import List, Optional, Tuple
from pydantic import BaseModel
from datetime import datetime


# 채팅 방에 제공될 내부 건축물 정보
class HeritageBuildingInfo(BaseModel):
    building_id: int
    name: str
    coordinate: Tuple[float, float] = (0, 0)

# 채팅 방에 제공될 내부 건축물 경로 정보    
class HeritageRouteInfo(BaseModel):
    route_id: int
    name: str
    buildings: List[HeritageBuildingInfo]

# 건축물 정보 버튼에 제공될 내부 건축물 정보 요청 값
class BuildingInfoButtonRequest(BaseModel): 
    building_id: int

# 건축물 정보 버튼에 제공될 내부 건축물 정보 응답 값
class BuildingInfoButtonResponse(BaseModel):
    image_url: Optional[str] = None
    bot_response: Optional[str] = None

# 퀴즈 버튼에 제공될 퀴즈 정보 요청 값
class BuildingQuizButtonRequest(BaseModel):
    building_id: int

# 퀴즈 버튼에 제공될 퀴즈 정보 응답 값
class BuildingQuizButtonResponse(BaseModel):
    question: str
    options: List[str]
    answer: int
    explanation: str
    quiz_count : int

# 건축물 추천 질문 요청 값
class RecommendedQuestionRequest(BaseModel):
    building_id: int

# 건축물 추천 질문 응답 값
class RecommendedQuestionResponse(BaseModel):
     building_id: int
     questions: List[str]

# 건축물 리스트 응답 값
class HeritageListResponse(BaseModel):
    id: int
    name: str
    location: str
    heritage_type: Optional[str]
    image_url: Optional[str]
    distance: Optional[float]

    class Config:
        from_attributes = True

# 건축물 페이지네이션 응답 값
class PaginatedHeritageResponse(BaseModel):
    items: List[HeritageListResponse]
    total_count : int
    page: int
    limit: int

class HeritageDetailResponse(BaseModel):
    id: int
    image_url: Optional[str] = None
    name: str
    name_hanja: Optional[str] = None
    description: Optional[str] = None
    heritage_type: Optional[str] = None
    category: Optional[str] = None
    sub_category1: Optional[str] = None
    sub_category2: Optional[str] = None
    era: Optional[str] = None
    location: Optional[str] = None

    class Config:
        from_attributes = True
