from __future__ import annotations

from .base import Base, generate_uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, UniqueConstraint

class Skill(Base):
    __tablename__ = "skills"
    __table_args__ = (UniqueConstraint('user_id', 'skill_name_id', name='uq_user_skill'),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'), nullable=False)
    skill_name_id: Mapped[str] = mapped_column(String, ForeignKey('skill_names.id'), nullable=False)
    category_id: Mapped[str] = mapped_column(String, ForeignKey('categories.id'), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # relationships - use string names here to avoid circular imports
    user: Mapped["User"] = relationship('User', back_populates='skills')
    skill_name: Mapped["SkillName"] = relationship('SkillName', back_populates='skills')
    category: Mapped["Category"] = relationship('Category', back_populates='skills')

    def __repr__(self):
        name = self.skill_name.name if self.skill_name else "Unknown"
        return f"<Skill {name} by user {self.user_id}>"
