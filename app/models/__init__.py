# Import base first
from .base import db

# Import enums before models that use them
from .enums import RequestStatus, SwapStatus, MessageType

# Import models in dependency order
from .user import User
from .category import Category
from .skill_name import SkillName
from .skill import Skill
from .swap import Swap
from .swap_conversation import SwapConversation
from .swap_message import SwapMessage
from .swap_request import SwapRequest
from .discuss_request import DiscussRequest

# Export all models
__all__ = [
    'db',
    'User',
    'Category',
    'SkillName',
    'Skill',
    'Swap',
    'SwapConversation',
    'SwapMessage',
    'SwapRequest',
    'DiscussRequest',
    'RequestStatus',
    'SwapStatus',
    'MessageType'
]