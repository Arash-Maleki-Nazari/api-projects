"""Database repository for CRUD operations."""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from src.database.models import Product, Label, LabelingHistory
from src.core.logger import logger


class ProductRepository:
    """Repository for Product model operations."""

    @staticmethod
    def create_product(db: Session, **kwargs) -> Product:
        """Create a new product."""
        product = Product(**kwargs)
        db.add(product)
        db.commit()
        db.refresh(product)
        logger.info(f"Product created: {product.id}")
        return product

    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
        """Get product by ID."""
        return db.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def list_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
        """List all products with pagination."""
        return db.query(Product).offset(skip).limit(limit).all()


class LabelRepository:
    """Repository for Label model operations."""

    @staticmethod
    def create_label(db: Session, product_id: int, label_type: str, label_value: str,
                     confidence: float = 0.0, metadata: dict = None) -> Label:
        """Create a new label."""
        label = Label(
            product_id=product_id,
            label_type=label_type,
            label_value=label_value,
            confidence=confidence,
            metadata=metadata,
        )
        db.add(label)
        db.commit()
        db.refresh(label)
        logger.info(f"Label created: {label.id}")
        return label

    @staticmethod
    def get_labels_by_product(db: Session, product_id: int, label_type: str = None) -> List[Label]:
        """Get labels for a product, optionally filtered by type."""
        query = db.query(Label).filter(Label.product_id == product_id)
        if label_type:
            query = query.filter(Label.label_type == label_type)
        return query.all()


class LabelingHistoryRepository:
    """Repository for LabelingHistory model operations."""

    @staticmethod
    def create_history(
        db: Session,
        product_id: int,
        input_payload: dict,
        output_payload: dict,
        service_name: str,
        processing_time_ms: float,
        api_key_used: str = None,
        error_message: str = None,
        trace_id: str = None,
    ) -> LabelingHistory:
        """Create a new history record."""
        history = LabelingHistory(
            product_id=product_id,
            input_payload=input_payload,
            output_payload=output_payload,
            service_name=service_name,
            processing_time_ms=processing_time_ms,
            api_key_used=api_key_used,
            error_message=error_message,
            trace_id=trace_id,
        )
        db.add(history)
        db.commit()
        db.refresh(history)
        logger.info(f"History record created for {service_name}: {history.id}")
        return history

    @staticmethod
    def get_history_by_trace_id(db: Session, trace_id: str) -> Optional[LabelingHistory]:
        """Get history record by trace ID."""
        return db.query(LabelingHistory).filter(LabelingHistory.trace_id == trace_id).first()

    @staticmethod
    def list_recent_history(db: Session, service_name: str = None, limit: int = 100) -> List[LabelingHistory]:
        """Get recent history records."""
        query = db.query(LabelingHistory)
        if service_name:
            query = query.filter(LabelingHistory.service_name == service_name)
        return query.order_by(desc(LabelingHistory.created_at)).limit(limit).all()
