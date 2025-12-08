from collections.abc import Generator
import os
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

# Load test environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env.test'))

from app.core.config import settings
from app.core.db import init_db
from app.api.deps import get_db
from app.main import app
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers


@pytest.fixture(name="session", scope="function")
def session_fixture() -> Generator[Session, None, None]:
    """
    Create a fresh database session for each test.
    Uses in-memory SQLite for speed and isolation.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # Initialize database with superuser for tests
        init_db(session)
        yield session


@pytest.fixture(name="client", scope="function")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """
    Create a test client that uses the test database session.
    """
    def get_db_override():
        return session

    app.dependency_overrides[get_db] = get_db_override
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture(name="db", scope="function")
def db_fixture(session: Session) -> Generator[Session, None, None]:
    """
    Alias for session fixture for backward compatibility.
    """
    yield session


@pytest.fixture(scope="function")
def superuser_token_headers(client: TestClient, session: Session) -> dict[str, str]:
    """
    Get authentication headers for superuser.
    """
    return get_superuser_token_headers(client)


@pytest.fixture(scope="function")
def normal_user_token_headers(client: TestClient, session: Session) -> dict[str, str]:
    """
    Get authentication headers for normal test user.
    """
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=session
    )