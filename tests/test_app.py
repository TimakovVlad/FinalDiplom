import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from products.models import Product, Category
from orders.models import Cart, CartItem, Order, Contact

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
def category():
    """Фикстура для категории."""
    return Category.objects.create(name='Electronics')

@pytest.fixture
def product(category):
    """Фикстура для продукта."""
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
def test_add_product_to_cart(api_client, user, product):
    """Тест добавления товара в корзину."""
    api_client.force_authenticate(user=user)
    response = api_client.post('/api/orders/cart/', {
    'product_id': product.id,
    'quantity': 2
    })
    assert response.status_code == 201
    assert response.data['message'] == 'Item added to cart'

@pytest.mark.django_db
def test_create_order(api_client, user, contact, product):
    """Тест создания заказа на основе корзины."""
    api_client.force_authenticate(user=user)

    # Добавляем товар в корзину
    Cart.objects.create(user=user)
    cart_item = CartItem.objects.create(cart=user.cart.first(), product=product, quantity=1)

    # Создаем заказ
    response = api_client.post('/api/orders/create-from-cart/', {
    'contact_id': contact.id
    })
    assert response.status_code == 201
    assert 'id' in response.data

@pytest.mark.django_db
def test_product_crud(api_client, user, category):
    """Тест CRUD операций с продуктами."""
    api_client.force_authenticate(user=user)
    assert user.is_active  # Убедимся, что пользователь активен

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

    # Проверяем получение списка продуктов
    response = api_client.get('/api/products/')
    assert response.status_code == 200
    assert len(response.data) > 0
