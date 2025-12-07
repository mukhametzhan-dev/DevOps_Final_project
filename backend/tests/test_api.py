import pytest
from fastapi.testclient import TestClient
from app.main import app

# --- ФИКСТУРЫ (Настройка окружения) ---
@pytest.fixture(scope="module")
def client():
    """Создает тестовый клиент FastAPI."""
    with TestClient(app) as client:
        yield client

# Тест 1: Проверка публичного эндпоинта (200 OK)
def test_get_api_status(client: TestClient):
    response = client.get("/api/v1/")
    assert response.status_code == 200
    # Проверяем, что ответ - это JSON с {"status":"ok"}
    assert response.json() == {"status": "ok"} 
    # ИЛИ, если вы хотите проверить только статус-код и что это не Swagger
    # assert response.json()["status"] == "ok"

# Тест 2: Проверка доступа к защищенному эндпоинту без токена (401 Unauthorized)
def test_access_protected_route_unauthorized(client: TestClient):
    """Тестирует, что доступ к защищенному маршруту без токена
       возвращает код 401 Unauthorized.
    """
    # Этот путь должен быть защищен (например, просмотр списка товаров)
    protected_path = "/api/v1/items/"
    
    response = client.get(protected_path)
    
    # Ожидаем код 401 (Не авторизован)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

# Тест 3: Создание нового пользователя через открытый эндпоинт
def test_create_new_user(client: TestClient):
    """Тестирует успешное создание нового пользователя через публичный роут."""
    new_user_data = {
        "email": "testuser@example.com",
        "password": "testpassword123",
        "is_active": True,
        "is_superuser": False,
        "full_name": "Test User"
    }
    
    registration_path = "/api/v1/users/signup"
    
    response = client.post(registration_path, json=new_user_data)
    
    # Ожидаем 200 OK или 201 Created (в зависимости от реализации FastAPI)
    assert response.status_code in (200, 201)
    
    # Проверяем, что ответ содержит данные пользователя (без пароля)
    response_data = response.json()
    assert response_data["email"] == "testuser@example.com"
    assert "password" not in response_data