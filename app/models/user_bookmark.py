from sqlalchemy import DECIMAL, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class UserBookmark(Base):
    __tablename__ = "user_bookmarks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    heritage_id = Column(Integer, ForeignKey("heritages.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="bookmarks")
    heritages = relationship("Heritage", back_populates="bookmarks")
