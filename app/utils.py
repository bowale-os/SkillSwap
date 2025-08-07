from flask import session
from typing import Optional
from app.models import db, User

def get_current_user() -> Optional[User]:
    """
    Retrieve the currently logged-in user from the session.

    Returns:
        User object if logged in, else None.
    """
    user_id = session.get('user_id')
    if not user_id:
        return None
    return db.session.get(User, user_id)
