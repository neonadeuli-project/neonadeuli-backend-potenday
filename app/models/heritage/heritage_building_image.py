from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class HeritageBuildingImage(Base):
    __tablename__ = "heritage_building_images"
    id = Column(Integer, primary_key=True, index=True)
    heritage_id = Column(Integer, ForeignKey("heritages.id"))
    building_id = Column(Integer, ForeignKey("heritage_buildings.id"))
    image_url = Column(String(255))
    description = Column(String(255))
    alt_text = Column(String(100))
    image_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    buildings = relationship("HeritageBuilding", back_populates="images")
    heritages = relationship("Heritage", back_populates="building_images")
