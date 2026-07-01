"""SQLAlchemy ORM models for database entities."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Product(Base):
    """Product model representing an e-commerce product."""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    inventory = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Label(Base):
    """Label model representing a label assigned to a product."""

    __tablename__ = "labels"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False, index=True)
    label_type = Column(String(50), nullable=False)  # 'category', 'recommendation'
    label_value = Column(String(255), nullable=False)
    confidence = Column(Float, default=0.0)
    label_metadata = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class LabelingHistory(Base):
    """LabelingHistory model for audit trail of labeling operations."""

    __tablename__ = "labeling_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False, index=True)
    input_payload = Column(JSON, nullable=False)
    output_payload = Column(JSON, nullable=False)
    service_name = Column(String(100), nullable=False)  # 'category_classifier', 'recommendation_scorer'
    processing_time_ms = Column(Float, nullable=False)
    api_key_used = Column(String(50), nullable=True)  # Masked API key for audit
    error_message = Column(Text, nullable=True)
    trace_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
