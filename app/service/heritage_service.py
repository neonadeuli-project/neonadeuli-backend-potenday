import logging

from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from haversine import haversine

from app.error.heritage_exceptions import DatabaseConnectionError, HeritageNotFoundException, InvalidCoordinatesException
from app.models.enums import EraCategory, SortOrder
from app.repository.heritage_repository import HeritageRepository
from app.schemas.heritage import HeritageDetailResponse, HeritageListResponse, PaginatedHeritageResponse
from app.utils.common import parse_location_for_detail, parse_location_for_list
from app.core.config import settings

logger = logging.getLogger(__name__)

class HeritageService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.heritage_repository = HeritageRepository(db)

    # 문화재 리스트 조회
    async def get_heritages(
            self, 
            page: int, 
            limit: int, 
            user_latitude: float, 
            user_longitude: float,
            name: Optional[str] = None,
            area_code: Optional[int] = None,
            heritage_type: Optional[int] = None,
            distance_range: Optional[str] = None,
            era_category: Optional[EraCategory] = None,
            sort_by: str = "id",
            sort_order: SortOrder = SortOrder.ASC
    ) -> PaginatedHeritageResponse:
        try:
            offset = (page - 1) * limit
            heritages, total_count = await self.heritage_repository.search_heritages(
                limit, 
                offset, 
                user_latitude, 
                user_longitude,
                name,
                area_code,
                heritage_type,
                distance_range,
                era_category,
                sort_by,
                sort_order,
                count_total=True
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_heritages: {str(e)}")
            raise DatabaseConnectionError()

        heritage_list = [
            HeritageListResponse(
                id = heritage.id,
                name = heritage.name,
                location = parse_location_for_list(heritage.location),
                heritage_type = heritage.heritage_types.name if heritage.heritage_types else "Unknown",
                image_url = heritage.image_url or settings.DEFAULT_IMAGE_URL,
                distance = round(distance, 1) if distance is not None else None
            )
            for heritage, distance in heritages
        ]

        return PaginatedHeritageResponse(
            items=heritage_list,
            total_count=total_count,
            page=page,
            limit=limit
        )
    
    # 문화재 상세 조회
    async def get_heritage_by_id(self, heritage_id: int) -> HeritageDetailResponse:
        try:
            heritage = await self.heritage_repository.get_heritage_by_id(heritage_id)
            if not heritage:
                raise HeritageNotFoundException(heritage_id)
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_heritage_detail: {str(e)}")
            raise DatabaseConnectionError()
        
        return HeritageDetailResponse (
            id = heritage.id,
            image_url = heritage.image_url,
            name = heritage.name,
            name_hanja = heritage.name_hanja,
            description = heritage.description,
            heritage_type = heritage.heritage_types.name if heritage.heritage_types else None,
            category = heritage.category,
            sub_category1 = heritage.sub_category1,
            sub_category2 = heritage.sub_category2,
            era = heritage.era,
            location = parse_location_for_detail(heritage.location)
        )