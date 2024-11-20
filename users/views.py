from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError

User = get_user_model()

class RegisterUserView(APIView):
    # Регистрация доступна для всех
    permission_classes = [AllowAny]

    def post(self, request):
        # Получаем данные из запроса
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        # Проверяем наличие обязательных полей
        if not username or not email or not password:
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Проверка на существование пользователя
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Проверяем пароль на валидность
        try:
            validate_password(password)
        except ValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        # Создаем пользователя
        user = User.objects.create_user(username=username, email=email, password=password)
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
