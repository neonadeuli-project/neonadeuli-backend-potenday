import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.error.heritage_exceptions import BuildingNotFoundException, HeritageNotFoundException
from app.error.image_exception import (
    ImageDeleteException, 
    ImageNotFoundException, 
    NoImagesFoundException
)
from app.models.heritage.heritage import Heritage
from app.models.heritage.heritage_building import HeritageBuilding
from app.models.heritage.heritage_building_image import HeritageBuildingImage

logger = logging.getLogger(__name__)

class ImageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # 문화재 이미지 업데이트
    async def update_heritage_image(self, heritage_id: int, image_url: str) -> Heritage:
        heritage = await self.db.execute(select(Heritage)
                                        .where(Heritage.id == heritage_id)
                                    )
        heritage = heritage.scalar_one_or_none()
        if not heritage:
            raise HeritageNotFoundException(heritage_id)
        
        heritage.image_url = image_url
        await self.db.commit()
        return heritage

    # 내부 건축물 이미지 추가
    async def add_building_image(self, heritage_id: int, building_id: int, image_url: str, description: str, alt_text: str) -> HeritageBuildingImage:
        # 내부 건축물 조회
        building = await self.db.execute(select(HeritageBuilding)
                                         .where(
                                             (HeritageBuilding.id == building_id) &
                                             (HeritageBuilding.heritage_id == heritage_id)
                                          )
                                        )
        building = building.scalar_one_or_none()
        if not building:
            raise BuildingNotFoundException(building_id)

        # 건축물 이미지 저장
        new_image = HeritageBuildingImage (
            heritage_id=heritage_id,
            building_id=building_id,
            image_url=image_url,
            description=description,
            alt_text=alt_text
        )

        self.db.add(new_image)
        await self.db.commit()
        await self.db.refresh(new_image)
        return new_image

    # 내부 건축물 이미지 조회
    async def get_building_images(self, heritage_id: int, building_id: int) -> List[HeritageBuildingImage]:
        result = await self.db.execute(select(HeritageBuildingImage)
                                       .join(HeritageBuilding)
                                       .where(
                                           (HeritageBuildingImage.building_id == building_id) &
                                           (HeritageBuilding.heritage_id == heritage_id)
                                        )
                                      )
        images = result.scalars().all()
        if not images:
            raise NoImagesFoundException(building_id)
        return images

    # 내부 건축물 이미지 삭제
    async def delete_building_image(self, image_id: int) -> HeritageBuildingImage:
        image = await self.db.get(HeritageBuildingImage, image_id)
        if not image:
            raise ImageNotFoundException(image_id)
        
        try:
            await self.db.delete(image)
            await self.db.execute
            return image
        except Exception as e:
            raise ImageDeleteException(image_id, str(e))