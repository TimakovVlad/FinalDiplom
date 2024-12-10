from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from social_django.utils import psa
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema
from .models import UserProfile
from .tasks import generate_thumbnail  # Задача для асинхронного создания миниатюр

User = get_user_model()

class RegisterUserView(APIView):
    """
    Регистрация пользователя с аватаром. Доступно для всех.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        request={
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "Имя пользователя"},
                "email": {"type": "string", "description": "Адрес электронной почты"},
                "password": {"type": "string", "description": "Пароль пользователя"},
                "avatar": {"type": "string", "format": "binary", "description": "Аватар пользователя (необязательно)"}
            },
            "required": ["username", "email", "password"]
        },
        responses={
            201: {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "Пользователь успешно зарегистрирован"}
                }
            },
            400: {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Все поля обязательны для заполнения"}
                }
            }
        }
    )
    def post(self, request):
        """
        Регистрация нового пользователя с аватаром (если передан).
        """
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        avatar = request.FILES.get('avatar')

        # Проверяем наличие обязательных полей
        if not username or not email or not password:
            return Response({'error': 'Все поля обязательны для заполнения'}, status=status.HTTP_400_BAD_REQUEST)

        # Проверка на существование пользователя
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Имя пользователя уже существует'}, status=status.HTTP_400_BAD_REQUEST)

        # Проверяем пароль на валидность
        try:
            validate_password(password)
        except ValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        # Создаем пользователя
        user = User.objects.create_user(username=username, email=email, password=password)

        # Создаем профиль пользователя и загружаем аватар, если он есть
        user_profile = UserProfile.objects.create(user=user)
        if avatar:
            user_profile.avatar = avatar
            user_profile.save()

            # Асинхронно генерируем миниатюры для аватара
            generate_thumbnail.delay(user_profile.avatar.path, size='small')
            generate_thumbnail.delay(user_profile.avatar.path, size='medium')
            generate_thumbnail.delay(user_profile.avatar.path, size='large')

        return Response({'message': 'Пользователь успешно зарегистрирован'}, status=status.HTTP_201_CREATED)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ChangePasswordView(APIView):
    """
    Изменение пароля пользователя. Доступно только для авторизованных пользователей.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "Пароль успешно изменен."
                    }
                }
            },
            400: {
                "type": "object",
                "properties": {
                    "old_password": {
                        "type": "string",
                        "example": "Неверный старый пароль."
                    }
                }
            }
        }
    )
    def patch(self, request):
        """Изменение пароля пользователя"""
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            # Проверяем, что старый пароль правильный
            if not user.check_password(old_password):
                raise ValidationError({"old_password": "Неверный старый пароль."})

            # Устанавливаем новый пароль
            user.set_password(new_password)
            user.save()

            return Response({"message": "Пароль успешно изменен."}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SocialLoginView(APIView):
    permission_classes = [AllowAny]

    @psa('social:complete')
    def post(self, request, backend):
        """Обработка аутентификации через социальные сети"""
        user = request.backend.do_auth(request.data.get('access_token'))
        if user:
            # Вы можете вернуть токен для дальнейшего использования
            return Response({"message": "Успешная аутентификация", "user": user.username}, status=status.HTTP_200_OK)
        return Response({"error": "Ошибка аутентификации"}, status=status.HTTP_400_BAD_REQUEST)
