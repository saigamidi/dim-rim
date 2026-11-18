"""Authentication service for user authentication and authorization."""
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models.user import User


class AuthService:
    """Service for authentication operations."""

    def __init__(self, session: Session):
        self.session = session

    def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticate user by email and password."""
        user = self.session.query(User).filter(User.email == email).first()
        
        if not user or not user.is_active:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user

    def get_user_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        return (
            self.session.query(User)
            .filter(User.id == user_id, User.is_active == True)  # noqa: E712
            .first()
        )

    def get_user_by_email(self, email: str) -> User | None:
        """Get user by email."""
        return (
            self.session.query(User)
            .filter(User.email == email, User.is_active == True)  # noqa: E712
            .first()
        )
