# db/models.py

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey
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

    # This line expects a matching Interview model with back_populates
    # interviews = relationship("Interview", back_populates="candidate", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="candidate", cascade="all, delete-orphan")



class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    score = Column(Float)
    summary = Column(String)

    candidate = relationship("Candidate", back_populates="interviews")
