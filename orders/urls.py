from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, CartViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'cart', CartViewSet, basename='cart')

# Подключаем маршруты
urlpatterns = [
    path('', include(router.urls)),
    path('orders/create-from-cart/', OrderViewSet.as_view({'post': 'create_from_cart'}), name='create-from-cart'),
]
