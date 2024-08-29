from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Float, 
    Enum
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import HeritageTypeName

class HeritageType(Base):
    __tablename__ = 'heritage_types'
    type_id = Column(Integer, primary_key=True)
    name = Column(String(50))
    type_name = Column(Enum(HeritageTypeName))
    default_radius = Column(Float)

    heritages = relationship("Heritage", back_populates="heritage_types")
    buildings = relationship("HeritageBuilding", back_populates="building_types")