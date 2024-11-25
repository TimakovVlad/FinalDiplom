from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('orders.urls')),  # Подключаем маршруты из приложения orders
    path('api/users/', include('users.urls')),  # Подключаем маршруты из приложения users
    path('api/products/', include('products.urls')),  # Подключаем маршруты для продуктов
]
