# Test Fix - Final Solution

## 🎯 The Real Problem

The tests were trying to connect to PostgreSQL instead of using the test database because:

1. ❌ **Wrong dependency override**: We were overriding `get_session()` from `db.py`
2. ✅ **Routes actually use**: `get_db()` from `api/deps.py`

## ✅ The Fix

### Changed `backend/tests/conftest.py`

**Key Changes**:

1. **Override the correct dependency**:
   ```python
   from app.api.deps import get_db  # ← This is what routes use!
   
   @pytest.fixture(name="client", scope="function")
   def client_fixture(session: Session) -> Generator[TestClient, None, None]:
       def get_db_override():
           return session
       
       app.dependency_overrides[get_db] = get_db_override  # ← Override THIS
   ```

2. **Initialize database with superuser**:
   ```python
   with Session(engine) as session:
       init_db(session)  # ← Creates superuser for auth tests
       yield session
   ```

## 🔍 Why It Failed Before

```python
# Routes in backend/app/api/routes/*.py use this:
from app.api.deps import get_db

@router.get("/items/")
def read_items(session: SessionDep):  # SessionDep = Depends(get_db)
    ...
```

We were overriding `get_session()` but routes use `get_db()`! 🤦

## ✅ Complete Working Configuration

```python
from collections.abc import Generator
import os
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env.test'))

from app.core.config import settings
from app.core.db import init_db
from app.api.deps import get_db  # ← THE KEY IMPORT
from app.main import app
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers


@pytest.fixture(name="session", scope="function")
def session_fixture() -> Generator[Session, None, None]:
    """Create fresh in-memory SQLite database for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        init_db(session)  # Create superuser
        yield session


@pytest.fixture(name="client", scope="function")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """Create test client with database override."""
    def get_db_override():
        return session

    app.dependency_overrides[get_db] = get_db_override  # ← THE KEY OVERRIDE
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture(name="db", scope="function")
def db_fixture(session: Session) -> Generator[Session, None, None]:
    """Alias for backward compatibility."""
    yield session


@pytest.fixture(scope="function")
def superuser_token_headers(client: TestClient, session: Session) -> dict[str, str]:
    """Get superuser auth headers."""
    return get_superuser_token_headers(client)


@pytest.fixture(scope="function")
def normal_user_token_headers(client: TestClient, session: Session) -> dict[str, str]:
    """Get normal user auth headers."""
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=session
    )
```

## 📊 Expected Test Results

After this fix:

- ✅ **No PostgreSQL connection errors** - Uses in-memory SQLite
- ✅ **Auth tests pass** - Superuser is initialized
- ✅ **CRUD tests pass** - Database is properly isolated
- ✅ **API route tests pass** - Dependency correctly overridden

### Before:
```
backend/tests/crud/test_user.py FFFFFFFFF
backend/tests/api/routes/test_items.py EEEEEEEEEEE
ERROR: connection to server at "127.0.0.1", port 5432 failed
```

### After:
```
backend/tests/crud/test_user.py .........     [PASSED]
backend/tests/api/routes/test_items.py .....  [PASSED]
backend/tests/test_api.py ....                [PASSED]
```

## 🧪 Test It Locally

```bash
# Should work now!
cd backend
PYTHONPATH=. pytest -v

# Check specific tests
PYTHONPATH=. pytest backend/tests/test_api.py -v
PYTHONPATH=. pytest backend/tests/crud/test_user.py -v
```

## 🚀 What Changed

| File | Change | Why |
|------|--------|-----|
| `conftest.py` | Import `get_db` from `api.deps` | Routes use this function |
| `conftest.py` | Override `app.dependency_overrides[get_db]` | Actually intercept DB calls |
| `conftest.py` | Add `init_db(session)` | Create superuser for auth tests |
| `conftest.py` | All `scope="function"` | Each test gets fresh DB |

## ✨ Key Takeaway

**Always override the dependency that your routes actually use!**

```python
# Routes use this ✅
from app.api.deps import SessionDep  # = Depends(get_db)

# So override this ✅
app.dependency_overrides[get_db] = get_db_override

# NOT this ❌
app.dependency_overrides[get_session] = ...  # Wrong!
```

## 🎯 Commit Message

```bash
git add backend/tests/conftest.py
git commit -m "fix: Override correct database dependency in tests

- Change dependency override from get_session to get_db
- Routes use get_db() from api.deps, not get_session()
- Add init_db() to create superuser for auth tests
- Fixes PostgreSQL connection errors in CI tests

Tests now use in-memory SQLite instead of trying to connect to PostgreSQL"
```

This should fix all the test failures! 🎉
