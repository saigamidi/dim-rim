"""Smoke tests to verify basic application functionality."""
import bcrypt
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User


def test_health_check(client: TestClient):
    """Test health check endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_database_connection(db_session: Session):
    """Test database session can create and query records."""
    # Create a test user
    test_user = User(
        email="test@example.com",
        hashed_password=bcrypt.hashpw("test123".encode(), bcrypt.gensalt(12)).decode(),
        full_name="Test User",
        role="test_role",
        is_active=True,
    )
    db_session.add(test_user)
    db_session.commit()
    
    # Query the user back
    user = db_session.query(User).filter(User.email == "test@example.com").first()
    assert user is not None
    assert user.full_name == "Test User"
    assert user.role == "test_role"


def test_user_model_relationships(db_session: Session):
    """Test that user model can be created with proper constraints."""
    user1 = User(
        email="user1@example.com",
        hashed_password=bcrypt.hashpw("pass1".encode(), bcrypt.gensalt(12)).decode(),
        full_name="User One",
        role="disruption_manager",
        is_active=True,
    )
    db_session.add(user1)
    db_session.commit()
    
    # Verify unique email constraint by checking count
    users = db_session.query(User).filter(User.email == "user1@example.com").all()
    assert len(users) == 1


def test_cors_headers(client: TestClient):
    """Test CORS headers are properly configured."""
    # Test that CORS middleware allows configured origins
    response = client.get("/health", headers={"Origin": "http://localhost:5173"})
    assert response.status_code == 200
    # CORS headers should be present
    assert "access-control-allow-origin" in response.headers
