from typing import List, Optional, Tuple
from fastapi import File, Form, UploadFile
from pydantic import BaseModel
from datetime import datetime

class ImageProcessingResponse(BaseModel):
    message: str

class HeritageBuildingImageResponse(BaseModel):
    id: int
    building_id: int
    image_url: str
    description: Optional[str] = None
    alt_text: Optional[str] = None
    image_order: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FindBuildingImageRequest(BaseModel):
    building_id: int

class FindBuildingImageResponse(BaseModel):
    images: List[HeritageBuildingImageResponse]

class DeleteBuildingImageRequest(BaseModel):
    image_id: int
