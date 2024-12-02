import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from products.models import Product, Category
from orders.models import Order, Address, Cart, CartItem, Contact

User = get_user_model()

@pytest.fixture
def api_client():
    """Фикстура для клиента API."""
    return APIClient()

@pytest.fixture
def user():
    """Фикстура для создания тестового пользователя."""
    return User.objects.create_user(username='testuser', email='test@example.com', password='password123')

@pytest.fixture
def auth_client(api_client, user):
    """Аутентифицированный клиент для запросов."""
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def product(db):
    """Фикстура для продукта."""
    category = Category.objects.create(name="Electronics")
    return Product.objects.create(
        name='Smartphone',
        description='A test smartphone',
        category=category,
        supplier='Test Supplier',
        price=999.99,
        quantity=10,
        parameters={"color": "black", "memory": "128GB"}
    )

@pytest.fixture
def category():
    """Фикстура для категории."""
    return Category.objects.create(name='Electronics')

@pytest.fixture
def contact(user):
    """Фикстура для контакта."""
    return Contact.objects.create(
        user=user,
        first_name="Test",
        last_name="User",
        phone="123456789",
        email="test@example.com",
        address="123 Test Street"
    )

@pytest.fixture
def cart(db, user, product):
    """Создание корзины с товарами."""
    cart = Cart.objects.create(user=user)
    cart.items.create(product=product, quantity=2)
    return cart

@pytest.mark.django_db
def test_register_user(api_client):
    """Тест регистрации нового пользователя."""
    response = api_client.post('/api/users/register/', {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'StrongPass123'
    })
    assert response.status_code == 201
    assert 'message' in response.data
    assert response.data['message'] == 'User created successfully'

@pytest.mark.django_db
def test_login_user(api_client, user):
    """Тест входа пользователя."""
    response = api_client.post('/api/users/login/', {
        'username': user.username,
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data


@pytest.mark.django_db
def test_create_order(api_client, user, contact, product):
    """Тест создания заказа на основе корзины."""
    api_client.force_authenticate(user=user)

    # Создаем корзину и добавляем товар
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=1)

    # Создаем заказ
    response = api_client.post('/api/orders/create-from-cart/', {
        'contact_id': contact.id
    })
    assert response.status_code == 201
    assert 'id' in response.data

    order_id = response.data["id"]
    order = Order.objects.get(id=order_id)
    assert order.status == 'new'  # Начальный статус
    assert order.contact == contact
    assert order.items.count() == 1
    assert order.items.first().product == product
    assert order.items.first().quantity == 1


@pytest.mark.django_db
def test_product_crud(api_client, user, category):
    """Тест CRUD операций с продуктами."""
    api_client.force_authenticate(user=user)

    # Создаем продукт
    response = api_client.post(
        '/api/products/',
        {
            'name': 'Laptop',
            'description': 'Test laptop',
            'category': category.id,
            'supplier': 'Test Supplier',
            'price': 1500.00,
            'quantity': 5,
            'parameters': {"color": "silver", "memory": "512GB"}
        },
        format='json',
        HTTP_ACCEPT='application/json'
    )
    assert response.status_code == 201
    product_id = response.data['id']

    # Проверяем получение списка продуктов
    response = api_client.get('/api/products/')
    assert response.status_code == 200
    assert len(response.data) > 0

    # Обновляем продукт
    response = api_client.put(
        f'/api/products/{product_id}/',
        {
            'name': 'Updated Laptop',
            'description': 'Updated description',
            'category': category.id,
            'supplier': 'Updated Supplier',
            'price': 1600.00,
            'quantity': 4,
            'parameters': {"color": "gold", "memory": "1TB"}
        },
        format='json',
        HTTP_ACCEPT='application/json'
    )
    assert response.status_code == 200  # Теперь проверим 200 OK, если все данные корректны

    # Удаляем продукт
    response = api_client.delete(f'/api/products/{product_id}/')
    assert response.status_code == 204


@pytest.mark.django_db
def test_product_filtering(api_client, user):
    """Тест фильтрации продуктов по имени."""
    api_client.force_authenticate(user=user)
    category = Category.objects.create(name="Electronics")
    Product.objects.create(name="Smartphone", description="High-end phone", price=799.99, quantity=10,
                           category=category)
    Product.objects.create(name="Laptop", description="Powerful laptop", price=1199.99, quantity=5, category=category)

    # Фильтрация по имени
    response = api_client.get('/api/products/?name=Smartphone')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Smartphone"


@pytest.mark.django_db
def test_product_search(api_client, user):
    """Тест поиска продуктов по описанию."""
    api_client.force_authenticate(user=user)  # Аутентификация пользователя
    category = Category.objects.create(name="Books")
    Product.objects.create(name="Python Programming", description="Learn Python", price=29.99, quantity=50,
                           category=category)
    Product.objects.create(name="Django Guide", description="Master Django", price=39.99, quantity=20,
                           category=category)

    # Поиск по описанию
    response = api_client.get('/api/products/?search=Python')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert "Learn Python" in response.data[0]["description"]


@pytest.mark.django_db
def test_status_transitions(auth_client, contact, cart):
    """Тест смены статусов заказа."""
    # Создаем заказ
    response = auth_client.post("/api/orders/create-from-cart/", {"contact_id": contact.id})
    assert response.status_code == 201, "Не удалось создать заказ."
    order_id = response.data["id"]

    # Проверяем начальный статус
    response = auth_client.get(f"/api/orders/orders/{order_id}/")
    assert response.status_code == 200
    assert response.data["status"] == "new"

    # Обновляем статус на 'confirmed'
    response = auth_client.patch(f"/api/orders/orders/{order_id}/change-status/", {"status": "confirmed"})
    assert response.status_code == 200
    print(response.data)
    assert response.data["status"] == "confirmed"

    # Обновляем статус на 'assembled'
    response = auth_client.patch(f"/api/orders/orders/{order_id}/change-status/", {"status": "assembled"})
    assert response.status_code == 200
    assert response.data["status"] == "assembled"

    # Обновляем статус на 'sent'
    response = auth_client.patch(f"/api/orders/orders/{order_id}/change-status/", {"status": "sent"})
    assert response.status_code == 200
    assert response.data["status"] == "sent"

    # Обновляем статус на 'delivered'
    response = auth_client.patch(f"/api/orders/orders/{order_id}/change-status/", {"status": "delivered"})
    assert response.status_code == 200
    assert response.data["status"] == "delivered"

    # Попытка изменить статус на уже завершенный заказ
    response = auth_client.patch(f"/api/orders/orders/{order_id}/change-status/", {"status": "confirmed"})
    print(response.data)  # Добавим вывод для отладки
    assert response.status_code == 400  # Ожидаем ошибку
