import logging

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.error.heritage_exceptions import (
    BuildingNotFoundException, 
    HeritageNotFoundException,
    InvalidAssociationException
)
from app.error.image_exception import (
    ImageException, 
    ImageNotFoundException, 
    ImageUploadException, 
    InvalidImageFormatException,
    NoImagesFoundException
)
from app.schemas.image import (
    FindBuildingImageRequest,
    FindBuildingImageResponse, 
    ImageProcessingResponse
)
from app.service.image_service import ImageService

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 문화재 이미지 업데이트
@router.post("/update-heritage", response_model=ImageProcessingResponse)
async def update_heritage_iamge(
    heritage_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    image_service = ImageService(db)
    try:
        result = await image_service.update_heritage_image(heritage_id, file)
        return ImageProcessingResponse (
            message="문화재 이미지가 성공적으로 업데이트 되었습니다."
        )
    except HeritageNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidImageFormatException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ImageUploadException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ImageException as e:
        raise HTTPException(status_code=400, detail=str(e))

# 건축물 이미지 추가
@router.post("/heritage/{heritage_id}/add-building", response_model=ImageProcessingResponse)
async def add_building_image(
    heritage_id: int,
    building_id: int = Form(...),
    file: UploadFile = File(...),
    description: str = Form(...),
    alt_text: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    image_service = ImageService(db)
    try:
        result = await image_service.add_building_image(
            heritage_id, 
            building_id, 
            file, 
            description, 
            alt_text
        )
        return ImageProcessingResponse (
            message="건축물 이미지가 성공적으로 추가되었습니다."
        )
    except BuildingNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidImageFormatException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ImageUploadException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ImageException as e:
        raise HTTPException(status_code=400, detail=str(e))

# 건축물 이미지 조회
@router.post("/heritage/{heritage_id}/find-building", response_model=FindBuildingImageResponse)
async def get_building_images(
    heritage_id: int,
    building_data: FindBuildingImageRequest,
    db: AsyncSession = Depends(get_db)
):
    image_service = ImageService(db)
    try:
        images = await image_service.get_building_image(heritage_id, building_data.building_id)
        return FindBuildingImageResponse(images=images)
    except InvalidAssociationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NoImagesFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"건축물 이미지 조회 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="서버 내부 오류 발생")

# 건축물 이미지 삭제
@router.post("/delete-building", response_model=ImageProcessingResponse)
async def delete_building_image(
    image_id: int, 
    db: AsyncSession = Depends(get_db)
):
    image_service = ImageService(db)
    try:
        result = await image_service.delete_building_image(image_id)
        return ImageProcessingResponse(
            message="건축물 이미지가 성공적으로 삭제되었습니다."
        )
    except ImageNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ImageException as e:
        raise HTTPException(status_code=400, detail=str(e))