import pytest
from rest_framework.test import APIClient
from factories import UserFactory, AddressFactory

@pytest.fixture
def auth_client():
    """Авторизованный клиент API."""
    user = UserFactory()
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def address_factory():
    """Фабрика адресов."""
    return AddressFactory

@pytest.fixture
def address(address_factory, auth_client):
    """Один тестовый адрес."""
    return address_factory(user=auth_client.handler._force_user)
