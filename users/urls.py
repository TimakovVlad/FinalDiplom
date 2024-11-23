from django.urls import path
from .views import RegisterUserView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', obtain_auth_token, name='login'),  # Получение токена
]
