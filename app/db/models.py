# db/models.py

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, func
from datetime import datetime
from app.db.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    role = Column(String)
    skills = Column(String)
    projects = Column(String)
    education = Column(String)
    achievements = Column(String)
    experience = Column(String)

    # ✅ Relationship to Interview
    interviews = relationship("Interview", back_populates="candidate", cascade="all, delete-orphan")

    # ✅ Optional: access all feedbacks through candidate
    interview_feedbacks = relationship("InterviewFeedback", back_populates="candidate")


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    score = Column(Float)
    summary = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # ✅ Relationships
    candidate = relationship("Candidate", back_populates="interviews")
    feedback_data = relationship("InterviewFeedback", back_populates="interview")



class InterviewFeedback(Base):
    __tablename__ = "interview_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    interview_id = Column(Integer, ForeignKey("interviews.id"))  # ✅ This must exist!
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)

    overall_feedback = Column(JSON, nullable=False)
    question_feedback = Column(JSON, nullable=False)

    candidate = relationship("Candidate", back_populates="interview_feedbacks")
    interview = relationship("Interview", back_populates="feedback_data")
