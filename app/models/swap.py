# app/models/swap.py
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum

from .base import Base, generate_uuid
from .enums import SwapStatus

class Swap(Base):
    __tablename__ = 'swaps'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'), nullable=False)
    offered_skill_id: Mapped[str] = mapped_column(String, ForeignKey('skills.id'), nullable=False)
    desired_skill_name_id: Mapped[str] = mapped_column(String, ForeignKey('skill_names.id'), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    status: Mapped[SwapStatus] = mapped_column(Enum(SwapStatus), default=SwapStatus.open)

    # Relationships — use string names here
    user: Mapped['User'] = relationship('User', back_populates='swaps')
    offered_skill: Mapped['Skill'] = relationship('Skill', foreign_keys=[offered_skill_id])
    desired_skill_name: Mapped['SkillName'] = relationship('SkillName', foreign_keys=[desired_skill_name_id])
    swap_conversations: Mapped[list['SwapConversation']] = relationship('SwapConversation', back_populates='swap')
    swap_requests: Mapped[list['SwapRequest']] = relationship('SwapRequest', back_populates='swap')
    discuss_requests: Mapped[list['DiscussRequest']] = relationship('DiscussRequest', back_populates='swap')

    def __repr__(self):
        return f"<Swap offering skill {self.offered_skill.skill_name.name} for {self.desired_skill_name.name}>"
