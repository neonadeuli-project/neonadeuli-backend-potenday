import logging
from typing import List
import uuid
from botocore.exceptions import ClientError
import boto3
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.error.heritage_exceptions import (
    BuildingNotFoundException,
    HeritageNotFoundException,
)
from app.error.image_exception import (
    ImageNotFoundException,
    ImageUploadException,
    InvalidImageFormatException,
    NoImagesFoundException,
    S3UploadException,
)
from app.models.heritage.heritage import Heritage
from app.models.heritage.heritage_building_image import HeritageBuildingImage
from app.repository.heritage_repository import HeritageRepository
from app.repository.image_repository import ImageRepository
from app.schemas.image import HeritageBuildingImageResponse
from app.service.s3_service import S3Service

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.heritage_repository = HeritageRepository(db)
        self.image_repository = ImageRepository(db)
        self.s3_service = S3Service()

    # 이미지 업로드
    async def upload_image(self, file: UploadFile) -> str:
        allowed_extensions = ["png", "jpg", "jpeg", "gif"]
        file_extension = file.filename.split(".")[-1].lower()

        if file_extension not in allowed_extensions:
            raise InvalidImageFormatException(
                file.filename, allowed_extensions
            )

        try:
            return await self.s3_service.upload_file(file, folder="images")
        except S3UploadException as e:
            raise ImageUploadException(file.filename, str(e))

    # 이미지 삭제
    # async def upload_image(self, file: UploadFile) -> str:
    #     try:
    #         contents = await file.read()
    #         self.s3_client.put_object(Bucket=settings.BUCKET_NAME, Key=file_name, Body=contents)
    #         return f"https://{settings.CDN_DOMAIN}/{settings.BUCKET_NAME}/{file_name}"
    #     except ClientError as e:
    #         raise ImageUploadException(file.filename, str(e))

    # 문화재 이미지 업데이트
    async def update_heritage_image(
        self, heritage_id: int, file: UploadFile
    ) -> Heritage:
        image_url = await self.upload_image(file)
        try:
            result = await self.image_repository.update_heritage_image(
                heritage_id, image_url
            )
            return result
        except HeritageNotFoundException:
            raise

    # 건축물 이미지 추가
    async def add_building_image(
        self,
        heritage_id: int,
        building_id: int,
        file: UploadFile,
        description: str,
        alt_text: str,
    ) -> HeritageBuildingImage:
        image_url = await self.upload_image(file)
        try:
            # 건축물과 문화재 유효성 검증
            belongs_to_heritage = await self.heritage_repository.verify_building_belongs_to_heritage(
                heritage_id, building_id
            )
            if not belongs_to_heritage:
                raise InvalidImageFormatException(
                    f"건축물 ID {building_id}번인 건축물은 문화재 ID {heritage_id}번인 문화재에 존재하지 않습니다."
                )

            # 이미지 저장
            result = await self.image_repository.add_building_image(
                heritage_id, building_id, image_url, description, alt_text
            )
            return result
        except BuildingNotFoundException:
            raise

    # 건축물 이미지 조회
    async def get_building_image(
        self, heritage_id: int, building_id: int
    ) -> List[HeritageBuildingImage]:
        try:
            # 건축물과 문화재 유효성 검증
            belongs_to_heritage = await self.heritage_repository.verify_building_belongs_to_heritage(
                heritage_id, building_id
            )
            if not belongs_to_heritage:
                raise InvalidImageFormatException(
                    f"건축물 ID {building_id}번인 건축물은 문화재 ID {heritage_id}번인 문화재에 존재하지 않습니다."
                )

            # 이미지 조회
            building_images = await self.image_repository.get_building_images(
                heritage_id, building_id
            )
            return [
                HeritageBuildingImageResponse.model_validate(image)
                for image in building_images
            ]
        except NoImagesFoundException:
            raise

    # 건축물 이미지 삭제
    async def delete_building_image(
        self, image_id: int
    ) -> HeritageBuildingImage:
        try:
            result = await self.image_repository.delete_building_image(
                image_id
            )
            return result
        except ImageNotFoundException:
            raise
