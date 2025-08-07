from .base import *
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

class Category(Base):
    __tablename__ = "categories"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    skills: Mapped[list['Skill']] = relationship('Skill', back_populates='category')

    def __repr__(self):
        skill_names = [skill.skill_name.name for skill in self.skills]
        return f"<Category {self.name} has skills {skill_names}>"
