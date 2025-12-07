from datetime import datetime, timedelta, timezone
from typing import Any
import os  

import jwt
from passlib.context import CryptContext

from backend.app.core.config import settings

# Определяем количество итераций для тестов
# Если мы в тестовой среде (проверяем, что pytest запускает тесты), используем 1 итерацию.
# В противном случае используем безопасное значение по умолчанию (например, 260000).
TEST_MODE = os.environ.get("PYTEST_CURRENT_TEST")

# Устанавливаем итерации: 1 для тестов, 260000 для продакшна
ITERATIONS = 1 if TEST_MODE else 260000 

# ИЗМЕНЕННЫЙ КОНТЕКСТ:
# Добавляем настройку pbkdf2_sha256__rounds
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"], 
    deprecated="auto",
    pbkdf2_sha256__rounds=ITERATIONS # <-- ЭТО УСКОРИТ ТЕСТЫ!
)


ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    # 2. УДАЛЕНО УСЕЧЕНИЕ: для pbkdf2_sha256 оно не требуется, 
    # так как у него нет ограничения в 72 байта.
    return pwd_context.hash(password)