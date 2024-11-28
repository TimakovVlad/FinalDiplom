from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/orders/', include('orders.urls')),  # Подключаем маршруты из приложения orders
    path('api/users/', include('users.urls')),  # Подключаем маршруты из приложения users
    path('api/products/', include('products.urls')),  # Подключаем маршруты для продуктов
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),  # Генерация схемы
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),  # Swagger UI
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),  # ReDoc
]
