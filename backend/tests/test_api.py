from fastapi.testclient import TestClient


# Тест 1: Health check endpoint
def test_health_check(client: TestClient):
    """Test that health check endpoint works."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


# Тест 2: Проверка публичного эндпоинта (200 OK)
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


# Тест 4: Documentation is accessible
def test_docs_accessible(client: TestClient):
    """Test that API documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200