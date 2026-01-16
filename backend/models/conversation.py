"""
Conversation model - chat history with the system
"""

from sqlalchemy import String, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional

from .base import Base, generate_uuid


class Conversation(Base):
    """
    Conversation history with the AI system.
    Stores messages and LangGraph state.
    """

    __tablename__ = "conversations"

    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)

    # Foreign key to fund (optional - may not have fund yet during creation)
    fund_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("funds.id"))

    # Phase
    phase: Mapped[Optional[str]] = mapped_column(String(20))  # creation, management

    # Messages (JSON array)
    messages: Mapped[Optional[dict]] = mapped_column(JSON)  # [{role, content, timestamp}, ...]

    # LangGraph state (JSON)
    state: Mapped[Optional[dict]] = mapped_column(JSON)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    fund: Mapped[Optional["Fund"]] = relationship("Fund", back_populates="conversations")

    def __repr__(self) -> str:
        return f"<Conversation(phase='{self.phase}')>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "fund_id": self.fund_id,
            "phase": self.phase,
            "messages": self.messages,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation"""
        if self.messages is None:
            self.messages = []

        # Create a new list to trigger SQLAlchemy change detection
        new_messages = list(self.messages)
        new_messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.messages = new_messages
