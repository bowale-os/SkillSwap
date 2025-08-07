from __future__ import annotations  # defer type hints evaluation

from .base import Base, generate_uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

class SkillName(Base):
    __tablename__ = 'skill_names'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    # Use string literal here to avoid circular import issues
    skills: Mapped[list["Skill"]] = relationship('Skill', back_populates='skill_name')

    def __repr__(self):
        return f"<SkillName {self.name}>"
