import pytest
from rest_framework.test import APIClient
from products.models import Category, Product
from django.contrib.auth import get_user_model


User = get_user_model()  # Получаем кастомную модель пользователя

@pytest.fixture
def api_client():
    client = APIClient()
    user = User.objects.create_user(username="testuser", password="password123")
    client.force_authenticate(user=user)  # Авторизуем клиента
    return client

@pytest.mark.django_db
def test_product_filtering(api_client):
    # Создаём тестовые категории и продукты
    category = Category.objects.create(name="Electronics")
    Product.objects.create(name="Smartphone", description="High-end phone", price=799.99, quantity=10, category=category)
    Product.objects.create(name="Laptop", description="Powerful laptop", price=1199.99, quantity=5, category=category)

    # Тестируем фильтрацию по имени
    response = api_client.get('/api/products/?name=Smartphone')  # Учитываем префикс
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['name'] == "Smartphone"


@pytest.mark.django_db
def test_product_search(api_client):
    # Создаём тестовые данные
    category = Category.objects.create(name="Books")
    Product.objects.create(name="Python Programming", description="Learn Python", price=29.99, quantity=50, category=category)
    Product.objects.create(name="Django Guide", description="Master Django", price=39.99, quantity=20, category=category)

    # Тестируем поиск по описанию
    response = api_client.get('/api/products/?search=Python')  # Учитываем префикс
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['name'] == "Python Programming"
