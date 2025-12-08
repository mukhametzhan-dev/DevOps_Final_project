from collections.abc import Generator
import os
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from httpx import AsyncClient # <-- ДОБАВИТЬ
from sqlmodel import Session, SQLModel, create_engine, delete

# Принудительная загрузка .env.test
# (Оставляем, чтобы настройки PROJECT_NAME и SECRET_KEY загружались)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env.test'))

from app.core.config import settings
from app.core.db import init_db  # <-- Убрали импорт 'engine' из db.py
from app.main import app
from app.models import Item, User
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers


# 1. ФИКСТУРА ENGINE (СОЗДАНИЕ SQLite DB ДЛЯ ТЕСТОВ)
# Эта фикстура создает и возвращает тестовый engine,
# а также создает все необходимые таблицы.
@pytest.fixture(scope="module", autouse=True)
def engine() -> Generator:
    # Используем SQLite File, который очистится в конце
    TEST_DATABASE_URL = "sqlite:///./test.db" 
    
    test_engine = create_engine(TEST_DATABASE_URL)
    
    # Создаем все таблицы (это имитирует миграции)
    SQLModel.metadata.create_all(test_engine)
    
    # Переопределяем engine приложения на тестовый engine для всех зависимостей
    # (Это важно, чтобы весь код, который вызывает engine, использовал тестовый)
    from app.core.db import engine as main_app_engine
    app.dependency_overrides[main_app_engine] = lambda: test_engine
    
    yield test_engine
    test_engine.dispose() 
    import time
    time.sleep(0.1)       
    os.remove("./test.db")

# 2. ФИКСТУРА SESSION (СЕАНС ДЛЯ ФИКСТУР)
# session теперь зависит от фикстуры engine выше
# conftest.py
@pytest.fixture(scope="function") # <--- Правильно, меняем на function!
def session_fixture(engine):
    """Предоставляет сессию с транзакцией и откатом для каждого теста."""
    connection = engine.connect()
    transaction = connection.begin()
    
    # Создаем сессию, привязанную к транзакции
    with Session(bind=connection) as session:
        yield session # Передаем сессию тесту
    
    # После теста: откат и закрытие
    transaction.rollback()
    connection.close()

# 3. ФИКСТУРА DB (СОЗДАНИЕ ПЕРВОНАЧАЛЬНЫХ ДАННЫХ И ОЧИСТКА)
# Эта фикстура запускает init_db (создание суперпользователя) и чистит данные
@pytest.fixture(scope="function", autouse=True)
def db(session_fixture: Session) -> None:
    # Инициализация DB (создание суперпользователя, если он нужен для тестов)
    init_db(session_fixture)
    
    # yield не нужен, так как очистка будет в фикстуре client (для модульных тестов)
    # или в самой фикстуре session, если это будет необходимо.
    # Оставляем только init_db для создания superuser.

# 4. ФИКСТУРА CLIENT (ТЕСТОВЫЙ КЛИЕНТ)
@pytest.fixture(scope="module")
async def client(session_fixture: Session) -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Очистка данных после каждого модуля тестов (или всех тестов, в зависимости от scope)
    with session_fixture:
        statement = delete(Item)
        session.exec(statement)
        statement = delete(User)
        session.exec(statement)
        session.commit()

# conftest.py (Добавить внизу)
@pytest.fixture(scope="function")
def session(session_fixture: Session) -> Generator[Session, None, None]:
    """Фикстура-псевдоним для совместимости со старыми тестами, которые запрашивают 'session'."""
    yield session_fixture

# --- ОСТАВШИЕСЯ ФИКСТУРЫ БЕЗ ИЗМЕНЕНИЙ ---

@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    # Примечание: тут используется 'db: Session' как параметр, но мы используем фикстуру session
    # Для простоты оставляем 'db: Session' (Pytest знает, что это наша фикстура session).
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )

@pytest.fixture(scope="session")
def anyio_backend():
    # Явно указываем использовать asyncio
    return "asyncio"

@pytest.fixture(scope="session")
def event_loop():
    # Создаем новый цикл событий для сессии
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()