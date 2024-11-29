from rest_framework.test import APIClient
import pytest
from django.contrib.auth import get_user_model
from orders.models import Order, Cart, Contact
from products.models import Product, Category

User = get_user_model()  # Получаем кастомную модель пользователя


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user(db):
    """Создание тестового пользователя."""
    return User.objects.create_user(username="testuser", password="testpass")


@pytest.fixture
def auth_client(api_client, test_user):
    """Аутентифицированный клиент для запросов."""
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def product(db):
    """Создание тестового продукта."""
    category = Category.objects.create(name="Electronics")
    return Product.objects.create(
        name="Smartphone",
        description="High-end phone",
        price=799.99,
        quantity=10,
        category=category
    )


@pytest.fixture
def contact(db, test_user):
    """Создание контактной информации для пользователя."""
    return Contact.objects.create(
        user=test_user,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="1234567890",
        address="123 Test Street"
    )


@pytest.fixture
def cart(db, test_user, product):
    """Создание корзины с товарами."""
    cart = Cart.objects.create(user=test_user)
    cart.items.create(product=product, quantity=2)
    return cart


@pytest.mark.django_db
def test_auto_generated_api_docs(auth_client):
    """Тест проверки доступности автогенерированной документации API."""
    response = auth_client.get("/api/docs/swagger/")
    assert response.status_code == 200, "Документация API недоступна."
    assert "swagger" in response.content.decode(), "Некорректный контент документации API."


@pytest.mark.django_db
def test_status_transitions(auth_client, contact, cart):
    """Тест смены статусов заказа."""
    # Создаём заказ из корзины
    response = auth_client.post("/api/orders/create-from-cart/", {"contact_id": contact.id})
    assert response.status_code == 201, "Не удалось создать заказ."
    order_id = response.data["id"]

    # Проверяем начальный статус заказа
    response = auth_client.get(f"/api/orders/orders/{order_id}/")
    assert response.status_code == 200, "Не удалось получить детали заказа."

    # Обновляем статус заказа на 'confirmed'
    response = auth_client.patch(f"/api/orders/orders/{order_id}/", {"status": "confirmed"})
    assert response.status_code == 200, "Не удалось обновить статус на 'confirmed'."
    assert response.data["status"] == "confirmed"

    # Обновляем статус заказа на 'assembled'
    response = auth_client.patch(f"/api/orders/orders/{order_id}/", {"status": "assembled"})
    assert response.status_code == 200, "Не удалось обновить статус на 'assembled'."
    assert response.data["status"] == "assembled"



@pytest.mark.django_db
def test_order_detail(auth_client, contact, cart):
    """Тест получения детальной информации о заказе."""
    # Создаём заказ из корзины
    response = auth_client.post("/api/orders/create-from-cart/", {"contact_id": contact.id})
    assert response.status_code == 201, "Не удалось создать заказ."
    order_id = response.data["id"]

    # Получаем детали заказа
    response = auth_client.get(f"/api/orders/orders/{order_id}/")
    assert response.status_code == 200, "Не удалось получить детали заказа."
    assert "items" in response.data, "Ответ не содержит информации о товарах."
    assert len(response.data["items"]) == 1, "Некорректное количество товаров в заказе."
    print(response.data)
    assert response.data["items"][0]["product_name"] == "Smartphone", "Некорректное название товара."

