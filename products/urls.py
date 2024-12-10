from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, ImportProductsView, TriggerErrorView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    path('import-products/', ImportProductsView.as_view(), name='import-products'),
    path('error/trigger-error/', TriggerErrorView.as_view(), name='trigger-error')
]
