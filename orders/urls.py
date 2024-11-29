from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, CartViewSet, AddressViewSet

# Создаём маршруты для ViewSet'ов
router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'addresses', AddressViewSet, basename='address')

# Подключаем маршруты
urlpatterns = [
    path('', include(router.urls)),  # Основные маршруты из ViewSet
    path('create-from-cart/', OrderViewSet.as_view({'post': 'create_from_cart'}), name='create-from-cart'),  # Доп. маршрут
]
