import pytest
from rest_framework.test import APIClient
from orders.models import Order, Cart, Contact
from products.models import Product, Category
from django.contrib.auth import get_user_model
from django.core.mail import send_mail


User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user(db):
    """Создание тестового пользователя."""
    return User.objects.create_user(username="testuser", password="testpass")


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
def test_send_email_confirmation(api_client, test_user, contact, cart):
    """Тестирование отправки email с подтверждением заказа."""
    # Аутентификация
    api_client.force_authenticate(user=test_user)

    # Создаем заказ из корзины
    response = api_client.post("/api/orders/create-from-cart/", {"contact_id": contact.id})

    # Проверяем, что заказ был успешно создан
    assert response.status_code == 201, "Не удалось создать заказ."

    # Проверяем, что в outbox был отправлен один email
    from django.core.mail import outbox
    assert len(outbox) == 1, "Email не был отправлен."

    # Проверяем, что тело письма содержит правильный текст
    email = outbox[0]
    assert "Ваш заказ №1 успешно подтвержден" in email.body
    assert "Товары в заказе: Smartphone" in email.body
    assert "Общая сумма: 1599.98" in email.body
