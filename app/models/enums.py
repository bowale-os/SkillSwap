import enum


class MessageType(enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"

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
