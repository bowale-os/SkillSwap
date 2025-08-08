from __future__ import annotations  # defer type hints evaluation

from .base import Base, generate_uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Boolean

class SwapConversation(Base):
    __tablename__ = 'swap_conversations'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    swap_id: Mapped[str] = mapped_column(String, ForeignKey('swaps.id'), nullable=False)
    sender_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'), nullable=False)  # person who started the convo
    recipient_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'), nullable=False)  # person who made the swap
    discuss_request_id: Mapped[str] = mapped_column(String, ForeignKey('discuss_requests.id'), nullable=True)  # new column
    
    # Acceptance tracking
    sender_accepted: Mapped[bool] = mapped_column(Boolean, default=False)
    recipient_accepted: Mapped[bool] = mapped_column(Boolean, default=False)

    swap: Mapped["Swap"] = relationship("Swap", back_populates="swap_conversations")

    discuss_request: Mapped["DiscussRequest"] = relationship(
    "DiscussRequest",
    back_populates="swap_conversation",
    uselist=False,
    foreign_keys=[discuss_request_id]
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
    
    @property
    def both_accepted(self):
        return self.sender_accepted and self.recipient_accepted
    
    def get_user_acceptance_status(self, user_id):
        """Get acceptance status for a specific user"""
        if user_id == self.sender_id:
            return self.sender_accepted
        elif user_id == self.recipient_id:
            return self.recipient_accepted
        return False
    
    def set_user_acceptance(self, user_id, accepted=True):
        """Set acceptance status for a specific user"""
        if user_id == self.sender_id:
            self.sender_accepted = accepted
        elif user_id == self.recipient_id:
            self.recipient_accepted = accepted
