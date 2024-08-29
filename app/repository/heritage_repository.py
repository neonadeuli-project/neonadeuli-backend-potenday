import json
import logging
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, and_, Float, update, values, join, tuple_, asc, desc
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, aliased

from app.models.chat.chat_session import ChatSession
from app.models.enums import EraCategory, SortOrder
from app.models.heritage.heritage_building_image import HeritageBuildingImage
from app.models.heritage.heritage_building import HeritageBuilding
from app.models.heritage.heritage_route import HeritageRoute
from app.models.heritage.heritage_route_building import HeritageRouteBuilding
from app.models.heritage.heritage import Heritage
from app.models.quiz import Quiz
from app.schemas.heritage import HeritageRouteInfo, HeritageBuildingInfo
from app.utils.common import parse_heritage_dist_range

logger = logging.getLogger(__name__)

class HeritageRepository:
    
    def __init__ (self, db: AsyncSession):
        self.db = db

    # 문화재 ID에 해당하는 문화재 조회
    async def get_heritage_by_id(self, heritage_id: int) -> Heritage:
        result = await self.db.execute(select(Heritage)
                                       .options(joinedload(Heritage.heritage_types))
                                       .where(Heritage.id == heritage_id))
        return result.unique().scalar_one_or_none()
    
    # 건축물 ID로 문화재 이름 조회
    async def get_heritage_building_name_by_id(self, building_id: int) -> str:
        result = await self.db.execute(select(HeritageBuilding.name)
                                       .where(HeritageBuilding.id == building_id)
                                    )
        return result.scalar_one_or_none()
    
    # 세션 ID로 문화재 ID 조회
    async def get_heritage_id_by_session(self, session_id: int) -> int:
        result = await self.db.execute(select(ChatSession.heritage_id)
                                       .where(ChatSession.id == session_id))
        heritage_id = result.scalar_one_or_none()
        if heritage_id is None:
            raise ValueError(f"세션 ID {session_id}에 대한 문화재 ID를 찾을 수 없습니다.")
        return heritage_id 
    
    # 문화재 ID로 문화재 이름 조회
    async def get_heritage_name_by_id(self, heritage_id: int) -> str:
        result = await self.db.execute(select(Heritage.name)
                                       .where(Heritage.id == heritage_id))
        heritage_name = result.scalar_one_or_none()
        if heritage_name is None:
            raise ValueError(f"문화재 ID {heritage_id}에 대한 이름을 찾을 수 없습니다.")
        return heritage_name

    # 문화재 건축물 ID 조회
    async def get_heritage_building_by_id(self, building_id: int) -> Optional[HeritageBuilding]:
        result = await self.db.execute(select(HeritageBuilding)
                                       .where(HeritageBuilding.id == building_id)
                                       .options(
                                           joinedload(HeritageBuilding.building_types),
                                           joinedload(HeritageBuilding.heritages))
                                        )
        return result.scalars().first()
    
    # 문화재 건축물 이미지 조회
    async def get_heritage_building_images(self, building_id: int) -> List[HeritageBuildingImage]:
        result = await self.db.execute(select(HeritageBuildingImage)
                                       .options(joinedload(HeritageBuildingImage.buildings))
                                       .where(HeritageBuildingImage.building_id == building_id)
                                       .order_by(HeritageBuildingImage.image_order))
        return result.scalars().all()
    
    # 문화재 건축물 코스 조회
    async def get_routes_with_buildings_by_heritages_id(self, heritage_id: int) -> List[HeritageRouteInfo]:
        result = await self.db.execute(select(HeritageRoute)
                                       .options(joinedload(HeritageRoute.route_buildings)
                                                .joinedload(HeritageRouteBuilding.buildings))
                                        .where(HeritageRoute.heritage_id == heritage_id))

        routes = result.unique().scalars().all()

        return [
            HeritageRouteInfo(
                route_id=route.id,
                name=route.name,
                buildings=[
                    HeritageBuildingInfo(
                        building_id=rb.buildings.id, 
                        name=rb.buildings.name,
                        coordinate=(rb.buildings.longitude, rb.buildings.latitude)
                    )
                    for rb in sorted(route.route_buildings, key=lambda x: x.visit_order)
                ]
            )
            for route in routes
        ]
    
    # 문화재 건축물 퀴즈 조회
    async def get_quiz_by_id(self, quiz_id: int):
        quiz = await self.db.execute(select(Quiz)
                                     .where(Quiz.id == quiz_id))
        return quiz.scalar_one_or_none()
    
    # 문화재 건축물 퀴즈 저장
    async def save_quiz_data(self, session_id: int, parsed_quiz: Dict[str, Any]):
        quiz = Quiz(
            session_id = session_id,
            question=parsed_quiz['question'],
            options=json.dumps(parsed_quiz['options'], ensure_ascii=False),
            answer=parsed_quiz['answer'],
            explanation=parsed_quiz['explanation']
        )
        self.db.add(quiz)
        await self.db.commit()
        await self.db.refresh(quiz)
        return quiz
    
    # 문화재에 속한 건축물 검증
    async def verify_building_belongs_to_heritage(self, heritage_id: int, building_id: int) -> bool:
        verified_building = await self.db.execute(select(HeritageBuilding)
                                                  .where(
                                                      (HeritageBuilding.id == building_id) &
                                                      (HeritageBuilding.heritage_id == heritage_id)
                                                  )
                                                )
        return verified_building.scalar_one_or_none() is not None
    
    async def search_heritages(
        self, 
        limit: int, 
        offset: int, 
        user_latitude: float,
        user_longitude: float,
        name: Optional[str] = None,
        area_code: Optional[int] = None,
        heritage_type: Optional[int] = None,
        distance_range: Optional[str] = None,
        era_category: Optional[EraCategory] = None,
        sort_by: str = "id",
        sort_order: SortOrder = SortOrder.ASC,
        count_total: bool = False
) -> Tuple[List[Tuple[Heritage, float]], int]:

        query = select(Heritage).options(joinedload(Heritage.heritage_types))

        # 거리 계산 표현식
        distance_expr = func.round(
            func.st_distance_sphere(
                func.point(func.cast(Heritage.longitude, Float), func.cast(Heritage.latitude, Float)),
                func.point(func.cast(user_longitude, Float), func.cast(user_latitude, Float))
            ) / 1000, 2
        ).label('distance')

        query = query.add_columns(distance_expr)

        # 이름 필터링
        if name:
            query = query.where(Heritage.name.like(f"%{name}%"))

        # 지역 필터링 (area_code None이 아닐 때만 적용)
        if area_code is not None:
            query = query.where(Heritage.area_code == area_code)

        # 문화재 유형 필터링
        if heritage_type is not None:
            query = query.where(Heritage.heritage_type_id.in_(heritage_type))

        # 시대 카테고리 필터링
        if era_category and era_category != EraCategory.ALL:
            query = query.filter(Heritage.era.like(f"%{era_category.value}"))

        # 정렬 로직 추가
        if sort_by == "distance":
            order_column = distance_expr
        else:
            order_column = Heritage.id
        
        if sort_order == SortOrder.ASC:
            query = query.order_by(asc(order_column))
        else:
            query = query.order_by(desc(order_column))

        # 전체 개수 계산
        if count_total:
            # count_query = query.with_only_columns(func.count()).order_by(None)
            total_count = await self.db.execute(select(func.count())
                                                .select_from(query.subquery())
                                            )
            total_count = total_count.scalar()
        else:
            total_count = 0

        # 거리 범위 필터링
        if distance_range:
            min_dist, max_dist = parse_heritage_dist_range(distance_range)
            query = query.where(and_(distance_expr >= min_dist, distance_expr < max_dist))

        # 페이지 네이션 적용
        query = query.limit(limit).offset(offset)

        logger.info(f"문화재 조회 SQL 쿼리가 생성되었습니다.: {query}")
        logger.info(f"쿼리 파라미터: user_latitude={user_latitude}, user_longitude={user_longitude}, area_code={area_code}, distance_range={distance_range}, limit={limit}, offset={offset}")
        
        try:
            result = await self.db.execute(query)
            heritages = result.unique().all()
            logger.info(f"쿼리 개수 결과 : {len(heritages)}")
            return heritages, total_count
        except Exception as e:
            logger.error(f"쿼리 실행 중 오류 발생: {str(e)}")
            raise