from __future__ import annotations  # defer type hints evaluation

from .base import Base, generate_uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey

class SwapConversation(Base):
    __tablename__ = 'swap_conversations'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    swap_id: Mapped[str] = mapped_column(String, ForeignKey('swaps.id'), nullable=False)
    sender_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'), nullable=False)  # person who started the convo
    recipient_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'), nullable=False)  # person who made the swap

    swap: Mapped["Swap"] = relationship("Swap", back_populates="swap_conversations")

    discuss_request: Mapped['DiscussRequest'] = relationship(
        "DiscussRequest",
        back_populates="swap_conversation",
        uselist=False
        )

    sender: Mapped["User"] = relationship("User", foreign_keys=[sender_id])
    recipient: Mapped["User"] = relationship("User", foreign_keys=[recipient_id])
    messages: Mapped[list["SwapMessage"]] = relationship(
        "SwapMessage",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )

    @property
    def participants(self):
        return [self.sender, self.recipient]
