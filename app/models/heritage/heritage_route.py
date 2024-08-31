from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Enum,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.enums import RouteType


class HeritageRoute(Base):
    __tablename__ = "heritage_routes"
    id = Column(Integer, primary_key=True, index=True)
    heritage_id = Column(Integer, ForeignKey("heritages.id"))
    name = Column(String(100))
    description = Column(Text)
    type = Column(Enum(RouteType))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    heritages = relationship("Heritage", back_populates="routes")
    route_buildings = relationship(
        "HeritageRouteBuilding", back_populates="routes"
    )
