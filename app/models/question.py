from enum import Enum

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class RecommendedQuestion(Base):
    __tablename__ = "recommended_questions"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    question = Column(String(255))

    chat_sessions = relationship("ChatSession", back_populates="recommended_questions")
