import pytest
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_create_address(auth_client):
    """Тест создания нового адреса доставки."""
    payload = {
        "title": "Дом",
        "address_line": "Улица Ленина, 10",
        "city": "Москва",
        "postal_code": "101000",
        "country": "Россия"
    }
    response = auth_client.post("/api/orders/addresses/", payload)
    assert response.status_code == HTTP_201_CREATED, "Адрес не был создан"
    data = response.json()
    assert data["title"] == payload["title"], "Название адреса не совпадает"
    assert data["city"] == payload["city"], "Город не совпадает"


@pytest.mark.django_db
def test_list_addresses(auth_client, address_factory):
    """Тест получения списка адресов."""
    address_factory.create_batch(3, user=auth_client.handler._force_user)
    response = auth_client.get("/api/orders/addresses/")
    assert response.status_code == HTTP_200_OK, "Не удалось получить список адресов"
    data = response.json()
    assert len(data) == 3, "Количество адресов не совпадает"


@pytest.mark.django_db
def test_update_address(auth_client, address):
    """Тест обновления адреса."""
    payload = {
        "title": "Работа",
        "address_line": "Проспект Мира, 20",
        "city": "Санкт-Петербург",
        "postal_code": "190000",
        "country": "Россия"
    }
    response = auth_client.put(f"/api/orders/addresses/{address.id}/", payload)
    assert response.status_code == HTTP_200_OK, "Не удалось обновить адрес"
    data = response.json()
    assert data["title"] == payload["title"], "Название адреса не обновлено"


@pytest.mark.django_db
def test_delete_address(auth_client, address):
    """Тест удаления адреса."""
    response = auth_client.delete(f"/api/orders/addresses/{address.id}/")
    assert response.status_code == HTTP_204_NO_CONTENT, "Адрес не был удалён"
    # Проверяем, что адрес удалён
    response = auth_client.get(f"/api/orders/addresses/{address.id}/")
    assert response.status_code == HTTP_404_NOT_FOUND, "Удалённый адрес доступен"
