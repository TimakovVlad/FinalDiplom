from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem, Cart, CartItem, Contact, Product
from .serializers import OrderSerializer, OrderItemSerializer, CartSerializer, CartItemSerializer
from products.models import Product
from .services import create_order_from_cart


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
        """Получение списка заказов пользователя"""
        queryset = self.filter_queryset(self.get_queryset().filter(user=request.user))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create_from_cart(self, request):
        """Создание заказа на основе корзины"""
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        contact_id = request.data.get('contact_id')
        try:
            contact = Contact.objects.get(id=contact_id, user=request.user)
        except Contact.DoesNotExist:
            return Response({'error': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)

        order = Order.objects.create(user=request.user, contact=contact)

        # Переносим элементы корзины в заказ
        total_amount = 0
        for cart_item in cart.items.all():
            order_item = OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            total_amount += order_item.quantity * order_item.price

        order.total_amount = total_amount
        order.save()

        # Очищаем корзину
        cart.items.all().delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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

        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': request.data.get('quantity', 1)}  # По умолчанию 1
        )

        if not created:
            # Если товар уже в корзине, увеличиваем количество
            cart_item.quantity += int(request.data.get('quantity', 1))
        else:
            cart_item.quantity = quantity
        cart_item.save()

        return Response({'message': 'Item added to cart'}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        """Обновление количества товара в корзине"""
        try:
            cart_item = CartItem.objects.get(pk=pk, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)

        quantity = request.data.get('quantity')
        if quantity is None or int(quantity) <= 0:
            return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = quantity
        cart_item.save()

        return Response({'message': 'Item quantity updated'}, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """Удаление товара из корзины"""
        try:
            cart_item = CartItem.objects.get(pk=pk, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()
        return Response({'message': 'Item removed from cart'}, status=status.HTTP_204_NO_CONTENT)


class AddToCartView(APIView):
    def post(self, request):
        user = request.user
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        # Проверяем, существует ли продукт
        product = get_object_or_404(Product, id=product_id)

        # Получаем или создаем корзину пользователя
        cart, created = Cart.objects.get_or_create(user=user)

        # Проверяем, есть ли этот продукт уже в корзине
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += int(quantity)
        else:
            cart_item.quantity = int(quantity)
        cart_item.save()

        return Response({"message": "Продукт успешно добавлен в корзину."}, status=status.HTTP_201_CREATED)

class CartView(APIView):
    def get(self, request):
        user = request.user
        cart = get_object_or_404(Cart, user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RemoveFromCartView(APIView):
    def delete(self, request, item_id):
        user = request.user
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=user)
        cart_item.delete()
        return Response({"message": "Продукт успешно удален из корзины."}, status=status.HTTP_200_OK)


class CreateOrderView(APIView):
    def post(self, request):
        user = request.user
        contact_id = request.data.get('contact_id')

        try:
            contact = Contact.objects.get(id=contact_id, user=user)
        except Contact.DoesNotExist:
            return Response({"error": "Контакт не найден."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = create_order_from_cart(user, contact)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Заказ успешно создан.", "order_id": order.id}, status=status.HTTP_201_CREATED)
