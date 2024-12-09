from django.urls import path, include
from .views import RegisterUserView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import ChangePasswordView, SocialLoginView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),  # Получение токена
    path('login/refresh/', TokenRefreshView.as_view(), name='login_refresh'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('auth/', include('social_django.urls', namespace='social')),  # Добавляем URL для социальных авторизаций
    path('auth/social/<backend>/', SocialLoginView.as_view(), name='social-login'),
]
