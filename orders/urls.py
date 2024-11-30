from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, CartView, AddToCartView, RemoveFromCartView, CartItemUpdateDeleteView, AddressViewSet, OrderDetailView

router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')

# Подключаем маршруты
urlpatterns = [
    path('', include(router.urls)),  # Подключаем все маршруты для AddressViewSet
    path('orders/', OrderViewSet.as_view({'get': 'list', 'post': 'create'}), name='orders-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/create-from-cart/', OrderViewSet.as_view({'post': 'create_from_cart'}), name='create-from-cart'),
    path('cart/', CartView.as_view(), name='cart-view'),
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/remove/<int:item_id>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('cart/update/<int:pk>/', CartItemUpdateDeleteView.as_view(), name='update-cart-item'),
    path('create-from-cart/', OrderViewSet.as_view({'post': 'create_from_cart'}), name='create-from-cart'),  # Доп. маршрут
]
