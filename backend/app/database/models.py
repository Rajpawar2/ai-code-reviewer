import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

def generate_uuid() -> str:
    return str(uuid.uuid4())

def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    repository_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    user = relationship("User", back_populates="projects")
    reviews = relationship("Review", back_populates="project", cascade="all, delete-orphan")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    source_type = Column(String(50), default="snippet", nullable=False)  # "snippet", "file_upload", "github_repo"
    filename = Column(String(255), default="code_snippet.py", nullable=False)
    source_code = Column(Text, nullable=False)
    
    # Scores
    overall_score = Column(Float, default=100.0, nullable=False)
    security_score = Column(Float, default=100.0, nullable=False)
    quality_score = Column(Float, default=100.0, nullable=False)
    performance_score = Column(Float, default=100.0, nullable=False)
    maintainability_score = Column(Float, default=100.0, nullable=False)

    ai_available = Column(Boolean, default=True, nullable=False)
    ai_summary = Column(Text, nullable=True)
    fixed_code = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False, index=True)

    user = relationship("User", back_populates="reviews")
    project = relationship("Project", back_populates="reviews")
    findings = relationship("Finding", back_populates="review", cascade="all, delete-orphan", order_by="Finding.line_number")
    files = relationship("ReviewFile", back_populates="review", cascade="all, delete-orphan")


class Finding(Base):
    __tablename__ = "findings"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    review_id = Column(String(36), ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, index=True)
    severity = Column(String(20), nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    category = Column(String(50), nullable=False)  # bug, security, performance, quality, maintainability, ast, lint, complexity
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    line_number = Column(Integer, default=0, nullable=False)
    recommendation = Column(Text, nullable=True)
    suggested_code = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    review = relationship("Review", back_populates="findings")

    __table_args__ = (
        Index("ix_findings_review_severity", "review_id", "severity"),
    )


class ReviewFile(Base):
    __tablename__ = "review_files"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    review_id = Column(String(36), ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    language = Column(String(50), default="python", nullable=False)
    lines_of_code = Column(Integer, default=0, nullable=False)
    complexity = Column(String(20), default="LOW", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    review = relationship("Review", back_populates="files")
