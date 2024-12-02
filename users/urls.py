from django.urls import path
from .views import RegisterUserView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import ChangePasswordView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),  # Получение токена
    path('login/refresh/', TokenRefreshView.as_view(), name='login_refresh'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]
