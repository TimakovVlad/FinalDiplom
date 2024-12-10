from rest_framework import viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.exceptions import APIException
from drf_spectacular.utils import extend_schema
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from .filters import ProductFilter
from rest_framework.permissions import IsAuthenticated
from products.tasks import import_products_from_yaml
from .tasks import create_product_thumbnail
import sentry_sdk

class CategoryViewSet(viewsets.ModelViewSet):
    """CRUD для категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class ProductViewSet(viewsets.ModelViewSet):
    """CRUD для продуктов"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    http_method_names = ['get', 'post', 'put', 'delete']

    @extend_schema(
        request=ProductSerializer,
        responses={201: ProductSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Добавление нового продукта"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # Сохраняем продукт
        product = serializer.save()

        # Если изображение присутствует, запускаем обработку в фоновом режиме
        if 'image' in request.data:
            image_path = product.image.path
            create_product_thumbnail.delay(image_path)  # Запускаем задачу Celery

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=ProductSerializer,
        responses={200: ProductSerializer}
    )
    def update(self, request, *args, **kwargs):
        """Обновление информации о продукте"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

class ImportProductsView(APIView):
    """Запуск импорта товаров из YAML"""
    permission_classes = [IsAdminUser]

    @extend_schema(
        request={
            "type": "object",
            "properties": {
                "yaml_path": {
                    "type": "string",
                    "description": "Путь к YAML-файлу с данными для импорта"
                }
            },
            "required": ["yaml_path"]
        },
        responses={
            202: {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "Импорт начат. Проверьте Celery задачи для статуса выполнения."
                    }
                }
            },
            400: {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Не указан путь к YAML-файлу"
                    }
                }
            }
        }
    )
    def post(self, request):
        yaml_path = request.data.get('yaml_path')
        if not yaml_path:
            return Response({"error": "Не указан путь к YAML-файлу"}, status=400)

        import_products_from_yaml.delay(yaml_path)
        return Response({"message": "Импорт начат. Проверьте Celery задачи для статуса выполнения."}, status=202)


class TriggerErrorView(APIView):
    """API View, который вызывает исключение для тестирования Sentry"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Искусственная ошибка
        division_by_zero = 1 / 0
        print(division_by_zero)
        return Response({"message": "Error triggered!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
