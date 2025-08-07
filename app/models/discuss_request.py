from .base import *
from .enums import *
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Enum


class DiscussRequest(Base):
    __tablename__ = 'discuss_requests'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    sender_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'), nullable=False)
    recipient_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'), nullable=False)
    swap_id: Mapped[str] = mapped_column(String, ForeignKey('swaps.id'), nullable=False)
    swap_conversation_id: Mapped[str] = mapped_column(String, ForeignKey('swap_conversations.id'), nullable=True)

    sender_skill_id: Mapped[str] = mapped_column(String, ForeignKey('skills.id'), nullable=False)
    recipient_skill_id: Mapped[str] = mapped_column(String, ForeignKey('skills.id'), nullable=False)

    status: Mapped[RequestStatus] = mapped_column(Enum(RequestStatus), default=RequestStatus.pending)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships - use string class names to avoid import issues
    sender: Mapped['User'] = relationship('User', foreign_keys=[sender_id], back_populates='sent_discuss_requests')
    recipient: Mapped['User'] = relationship('User', foreign_keys=[recipient_id], back_populates='received_discuss_requests')
    swap: Mapped['Swap'] = relationship('Swap', foreign_keys=[swap_id], back_populates='discuss_requests')
    
    swap_conversation: Mapped['SwapConversation'] = relationship(
        "SwapConversation",
        back_populates="discuss_request",
        uselist=False,
        foreign_keys=[swap_conversation_id]
    )
    
    sender_skill: Mapped['Skill'] = relationship('Skill', foreign_keys=[sender_skill_id])
    recipient_skill: Mapped['Skill'] = relationship('Skill', foreign_keys=[recipient_skill_id])

    def accept(self):
        self.status = RequestStatus.accepted

    def reject(self):
        self.status = RequestStatus.rejected

    def __repr__(self):
        return f"<DiscussRequest from {self.sender_id} to {self.recipient_id} for swap {self.swap_id} status={self.status}>"
