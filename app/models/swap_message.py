from __future__ import annotations  # defer type hints evaluation

from .base import Base, generate_uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum
from datetime import datetime, timezone
from .enums import MessageType

class SwapMessage(Base):
    __tablename__ = 'swap_messages'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    conversation_id: Mapped[str] = mapped_column(String, ForeignKey('swap_conversations.id'))
    sender_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'))
    recipient_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'))  # person who made the swap
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    type: Mapped[MessageType] = mapped_column(Enum(MessageType), default=MessageType.TEXT, nullable=False)

    conversation: Mapped["SwapConversation"] = relationship("SwapConversation", back_populates="messages")
    sender: Mapped["User"] = relationship("User", foreign_keys=[sender_id])
    recipient: Mapped["User"] = relationship("User", foreign_keys=[recipient_id])
