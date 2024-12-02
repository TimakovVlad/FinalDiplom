import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

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

@pytest.mark.django_db
def test_change_password(auth_client, user):
    """Тест изменения пароля пользователя"""
    old_password = 'oldPassword123'
    new_password = 'newPassword123'

    # Устанавливаем старый пароль для пользователя
    user.set_password(old_password)
    user.save()

    # Авторизуемся
    auth_client.login(username=user.username, password=old_password)

    # Меняем пароль
    response = auth_client.patch('/api/users/change-password/', {
        'old_password': old_password,
        'new_password': new_password
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == 'Пароль успешно изменен.'

    # Проверяем, что новый пароль работает
    user.refresh_from_db()
    assert user.check_password(new_password)
