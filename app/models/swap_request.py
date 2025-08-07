from __future__ import annotations
from .base import Base, generate_uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Enum
from datetime import datetime, timezone
from .enums import RequestStatus

class SwapRequest(Base):
    __tablename__ = 'swap_requests'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)

    sender_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'), nullable=False)
    recipient_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'), nullable=False)
    swap_id: Mapped[str] = mapped_column(String, ForeignKey('swaps.id'), nullable=False)

    sender_skill_id: Mapped[str] = mapped_column(String, ForeignKey('skills.id'), nullable=False)
    recipient_skill_id: Mapped[str] = mapped_column(String, ForeignKey('skills.id'), nullable=False)

    status: Mapped[RequestStatus] = mapped_column(Enum(RequestStatus), default=RequestStatus.pending)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Use string names for relationships to avoid circular imports
    sender: Mapped[User] = relationship('User', foreign_keys=[sender_id], back_populates='sent_swap_requests')
    recipient: Mapped[User] = relationship('User', foreign_keys=[recipient_id], back_populates='received_swap_requests')
    swap: Mapped[Swap] = relationship('Swap', foreign_keys=[swap_id], back_populates='swap_requests')

    sender_skill: Mapped[Skill] = relationship('Skill', foreign_keys=[sender_skill_id])
    recipient_skill: Mapped[Skill] = relationship('Skill', foreign_keys=[recipient_skill_id])

    def accept(self):
        """Accept the swap request and update related statuses"""
        self.status = RequestStatus.accepted
        # Update the swap status
        if self.swap:
            self.swap.update_status()
    
    def reject(self):
        """Reject the swap request and update related statuses"""
        self.status = RequestStatus.rejected
        # Update the swap status
        if self.swap:
            self.swap.update_status()
    
    def cancel(self):
        """Cancel the swap request and update related statuses"""
        self.status = RequestStatus.cancelled
        # Update the swap status
        if self.swap:
            self.swap.update_status()

    def __repr__(self):
        return f"<SwapRequest {self.sender_id} offers {self.sender_skill_id} for {self.recipient_skill_id}>"
