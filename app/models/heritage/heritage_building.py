from sqlalchemy import DECIMAL, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class HeritageBuilding(Base):
    __tablename__ = "heritage_buildings"
    id = Column(Integer, primary_key=True, index=True)
    heritage_id = Column(Integer, ForeignKey("heritages.id"))
    building_type_id = Column(Integer, ForeignKey("heritage_types.type_id"))
    name = Column(String(100))
    description = Column(Text)
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    custom_radius = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    building_types = relationship("HeritageType", back_populates="buildings")
    heritages = relationship("Heritage", back_populates="buildings")
    images = relationship("HeritageBuildingImage", back_populates="buildings")
    route_buildings = relationship("HeritageRouteBuilding", back_populates="buildings")
