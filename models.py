from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, Text, DateTime, ForeignKey, UniqueConstraint, event
from datetime import datetime, timezone
import uuid

import enum
from sqlalchemy import Enum

class RequestStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    cancelled = "cancelled"

class SwapStatus(enum.Enum):
    open = "open"
    in_discussion = "in_discussion"
    completed = "completed"
    cancelled = "cancelled"

class MessageType(enum.Enum):
    text = "text"
    system = "system"
    offer_update = "offer_update"

# UUID generator for primary keys
def generate_uuid() -> str:
    return str(uuid.uuid4())

# Base class using SQLAlchemy 2.0+
class Base(DeclarativeBase):
    pass

# SQLAlchemy instance with custom base
db = SQLAlchemy(model_class=Base)

# --- MODELS ---
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


    def __repr__(self):
        return f"<User {self.name}>"
    
class SkillName(Base):
    __tablename__ = 'skill_names'
    id :Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    name :Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    skills: Mapped[list['Skill']] = relationship('Skill', back_populates='skill_name')

    def __repr__(self):
        return f"<Skill {self.name}>"

class Category(Base):
    __tablename__ = "categories"
    id :Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    name :Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    skills: Mapped[list['Skill']] = relationship('Skill', back_populates='category')

    def __repr__(self):
        skill_names = [skill.skill_name.name for skill in self.skills]
        return f"<Category {self.name} has skills {skill_names}>"


class Skill(Base):
    __tablename__ = "skills"
    __table_args__ = (UniqueConstraint('user_id', 'skill_name_id', name='uq_user_skill'),)

    id :Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    user_id :Mapped[str] = mapped_column(String, ForeignKey('users.id'), nullable=False)
    skill_name_id :Mapped[str] = mapped_column(String, ForeignKey('skill_names.id'), nullable=False)
    category_id :Mapped[str] = mapped_column(String, ForeignKey('categories.id'), nullable=False)
    description :Mapped[str] = mapped_column(Text, nullable=False)

    #relationships
    user :Mapped['User'] = relationship('User', back_populates='skills')
    skill_name: Mapped['SkillName'] = relationship('SkillName', back_populates='skills')
    category: Mapped['Category'] = relationship('Category', back_populates='skills')

    def __repr__(self):
        name = self.skill_name.name if self.skill_name else "Unknown"
        return f"<Skill {name} by user {self.user_id}>"

     
class Swap(Base):
    __tablename__ = 'swaps'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'), nullable=False)
    offered_skill_id: Mapped[str] = mapped_column(String, ForeignKey('skills.id'), nullable=False)
    desired_skill_name_id: Mapped[str] = mapped_column(String, ForeignKey('skill_names.id'), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    status: Mapped[SwapStatus] = mapped_column(Enum(SwapStatus), default=SwapStatus.open) #after discussrequest

    # Relationships
    user: Mapped['User'] = relationship('User', back_populates='swaps')
    offered_skill: Mapped['Skill'] = relationship('Skill', foreign_keys=[offered_skill_id])
    desired_skill_name: Mapped['SkillName'] = relationship('SkillName', foreign_keys=[desired_skill_name_id])
    swap_conversations: Mapped[list['SwapConversation']] = relationship("SwapConversation", back_populates="swap")
    swap_requests: Mapped[list['SwapRequest']] = relationship("SwapRequest", back_populates='swap')
    discuss_requests: Mapped[list['DiscussRequest']] = relationship("DiscussRequest", back_populates="swap")

    def __repr__(self):
        return f"<Swap offering skill {self.offered_skill.skill_name.name} for {self.desired_skill_name.name}>"


    
class SwapRequest(Base):
    __tablename__ = 'swap_requests'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)

    sender_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'), nullable=False)
    recipient_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'), nullable=False)
    swap_id: Mapped[str] = mapped_column(String, ForeignKey('swaps.id'), nullable=False)
    

    sender_skill_id: Mapped[str] = mapped_column(String, ForeignKey('skills.id'), nullable=False)
    recipient_skill_id: Mapped[str] = mapped_column(String, ForeignKey('skills.id'), nullable=False)

    status: Mapped[RequestStatus] = mapped_column(Enum(RequestStatus), default=RequestStatus.pending) #after discussrequest
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    sender: Mapped['User'] = relationship('User', foreign_keys=[sender_id], back_populates='sent_swap_requests')
    recipient: Mapped['User'] = relationship('User', foreign_keys=[recipient_id], back_populates='received_swap_requests')
    swap: Mapped['Swap'] = relationship('Swap', foreign_keys=[swap_id], back_populates='swap_requests')

    sender_skill: Mapped['Skill'] = relationship('Skill', foreign_keys=[sender_skill_id])
    recipient_skill: Mapped['Skill'] = relationship('Skill', foreign_keys=[recipient_skill_id])

    def __repr__(self):
        return f"<SwapRequest {self.sender_id} offers {self.sender_skill_id} for {self.recipient_skill_id}>"


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

    # Relationships
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


class SwapConversation(Base):
    __tablename__ = 'swap_conversations'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    swap_id: Mapped[str] = mapped_column(String, ForeignKey('swaps.id'), nullable=False)
    discuss_request_id: Mapped[str]= mapped_column(String, ForeignKey('discuss_requests.id'), nullable=False)
    sender_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'), nullable=False)  # person who started the convo
    recipient_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'), nullable=False)  # person who made the swap

    swap: Mapped["Swap"] = relationship("Swap", back_populates="swap_conversations")

    discuss_request: Mapped['DiscussRequest'] = relationship(
        "DiscussRequest",
        back_populates="swap_conversation",
        uselist=False,
        foreign_keys=[DiscussRequest.swap_conversation_id]
    )   
    
    sender: Mapped["User"] = relationship("User", foreign_keys=[sender_id])
    recipient: Mapped["User"] = relationship("User", foreign_keys=[recipient_id])
    messages: Mapped[list["SwapMessage"]] = relationship("SwapMessage", back_populates="conversation", cascade="all, delete-orphan")

    @property
    def participants(self):
        return [self.sender, self.recipient]

class SwapMessage(Base):
    __tablename__ = 'swap_messages'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    conversation_id: Mapped[str] = mapped_column(String, ForeignKey('swap_conversations.id'))
    sender_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'))
    recipient_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'))  # person who made the swap
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    conversation: Mapped["SwapConversation"] = relationship("SwapConversation", back_populates="messages")
    sender: Mapped["User"] = relationship("User", foreign_keys=[sender_id])
    recipient: Mapped["User"] = relationship("User", foreign_keys=[recipient_id])

