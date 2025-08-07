# app/models/user.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime
from datetime import datetime, timezone

from .base import Base  # import the Base class
from .base import db    # import the SQLAlchemy instance
from .enums import RequestStatus, SwapStatus, MessageType  # import enums separately

from .skill import Skill
from .swap import Swap
from .swap_request import SwapRequest
from .discuss_request import DiscussRequest
from .swap_conversation import SwapConversation

import uuid

def generate_uuid() -> str:
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(60), nullable=False)
    email: Mapped[str] = mapped_column(String(60), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # relationships
    skills: Mapped[list['Skill']] = relationship("Skill", back_populates='user') 
    swaps: Mapped[list['Swap']] = relationship('Swap', back_populates='user')
    sent_swap_requests:Mapped[list['SwapRequest']] = relationship(
        "SwapRequest", 
        back_populates="sender",
        foreign_keys="[SwapRequest.sender_id]"
        )
    
    received_swap_requests: Mapped[list['SwapRequest']] = relationship(
        "SwapRequest", 
        back_populates="recipient",
        foreign_keys="[SwapRequest.recipient_id]"
        )
    
    sent_discuss_requests:Mapped[list['DiscussRequest']]= relationship(
    "DiscussRequest",
    back_populates="sender",
    foreign_keys="[DiscussRequest.sender_id]"
        )

    received_discuss_requests:Mapped[list['DiscussRequest']]= relationship(
        "DiscussRequest",
        back_populates="recipient",
        foreign_keys="[DiscussRequest.recipient_id]"
    )

    conversations_started: Mapped[list['SwapConversation']] = relationship(
        "SwapConversation",
        back_populates="sender",
        foreign_keys="[SwapConversation.sender_id]"
    )

    conversations_received: Mapped[list['SwapConversation']] = relationship(
        "SwapConversation",
        back_populates="recipient",
        foreign_keys="[SwapConversation.recipient_id]"
    )
