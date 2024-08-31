from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    Text,
    JSON,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.config import settings
from app.core.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    heritage_id = Column(Integer, ForeignKey("heritages.id"))
    heritage_name = Column(String(255))
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    quiz_count = Column(Integer, default=settings.QUIZ_COUNT)
    full_conversation = Column(Text)  # 전체 대화 내용 저장
    sliding_window = Column(Text)  # 슬라이딩 윈도우 내용 저장
    summary_keywords = Column(JSON)  # 요약 키워드 저장
    visited_buildings = Column(JSON)  # 방문한 건물 목록 저장
    summary_generated_at = Column(
        DateTime(timezone=True), nullable=True
    )  # 요약 생성 시간 추적
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    users = relationship("User", back_populates="chat_sessions")
    heritages = relationship("Heritage", back_populates="chat_sessions")
    chat_messages = relationship("ChatMessage", back_populates="chat_sessions")
    quizzes = relationship("Quiz", back_populates="chat_sessions")
    recommended_questions = relationship(
        "RecommendedQuestion", back_populates="chat_sessions"
    )
