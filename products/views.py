from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from rest_framework.permissions import IsAuthenticated
from products.tasks import import_products_from_yaml

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
    http_method_names = ['get', 'post', 'put', 'delete']

    def create(self, request, *args, **kwargs):
        """Добавление нового продукта"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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

    def post(self, request):
        yaml_path = request.data.get('yaml_path')
        if not yaml_path:
            return Response({"error": "Не указан путь к YAML-файлу"}, status=400)

        import_products_from_yaml.delay(yaml_path)
        return Response({"message": "Импорт начат. Проверьте Celery задачи для статуса выполнения."}, status=202)
