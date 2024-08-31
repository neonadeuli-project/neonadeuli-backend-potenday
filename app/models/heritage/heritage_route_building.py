from sqlalchemy import DECIMAL, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class HeritageRouteBuilding(Base):
    __tablename__ = "heritage_route_buildings"
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("heritage_routes.id"))
    building_id = Column(Integer, ForeignKey("heritage_buildings.id"))
    visit_order = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    routes = relationship("HeritageRoute", back_populates="route_buildings")
    buildings = relationship("HeritageBuilding", back_populates="route_buildings")
