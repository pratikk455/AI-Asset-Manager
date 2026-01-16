"""
Base model configuration for SQLAlchemy
"""

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func
from datetime import datetime
import uuid


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


def generate_uuid() -> str:
    """Generate a UUID string"""
    return str(uuid.uuid4())
