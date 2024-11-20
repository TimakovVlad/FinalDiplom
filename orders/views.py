from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Order, OrderItem, Cart, CartItem
from .serializers import OrderSerializer, OrderItemSerializer, CartSerializer, CartItemSerializer
from products.models import Product

class OrderViewSet(viewsets.ModelViewSet):
    # Определяем доступные методы для заказов
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]  # Только авторизованные пользователи

    def create(self, request, *args, **kwargs):
        # Переопределяем создание заказа
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        # Получение списка заказов пользователя
        queryset = self.filter_queryset(self.get_queryset().filter(user=request.user))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Получение текущей корзины пользователя"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def create(self, request):
        """Добавление товара в корзину"""
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity += quantity
        cart_item.save()

        return Response({'message': 'Item added to cart'}, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        """Удаление товара из корзины"""
        try:
            cart_item = CartItem.objects.get(pk=pk, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()
        return Response({'message': 'Item removed from cart'}, status=status.HTTP_204_NO_CONTENT)
