from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem, Cart, CartItem, Contact, Address
from .serializers import OrderSerializer, CartItemSerializer, AddressSerializer
from products.models import Product
from django.core.mail import send_mail
from drf_spectacular.utils import extend_schema


class OrderViewSet(viewsets.ModelViewSet):
    # Определяем доступные методы для заказов
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]  # Только авторизованные пользователи

    @extend_schema(
        responses={201: OrderSerializer}
    )
    def create(self, request, *args, **kwargs):
        # Переопределяем создание заказа
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(
        responses={200: OrderSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """Получение списка заказов текущего пользователя"""
        # Фильтруем заказы по текущему пользователю
        queryset = self.filter_queryset(self.get_queryset().filter(user=request.user))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        responses={200: OrderSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        """Получение деталей заказа по ID"""
        # Получаем заказ по pk, проверяя принадлежность к текущему пользователю
        order = self.get_object()
        if order.user != request.user:
            return Response({'error': 'Вы не можете просматривать этот заказ.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @extend_schema(
        responses={200: OrderSerializer}
    )
    @action(detail=True, methods=['patch'], url_path='change-status')
    def change_status(self, request, pk=None):
        """Изменение статуса заказа"""
        order = self.get_object()
        new_status = request.data.get('status')

        if not new_status:
            return Response({'error': 'Необходимо указать новый статус.'}, status=400)

        # Проверяем, что новый статус корректен
        valid_statuses = dict(Order._meta.get_field('status').choices)
        if new_status not in valid_statuses:
            return Response({'error': 'Некорректный статус.'}, status=400)

        try:
            order.change_status(new_status)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)

        return Response({'message': 'Статус успешно обновлен.', 'status': order.status})

    def send_order_confirmation_email(self, order):
        subject = f"Подтверждение заказа №{order.id}"
        details = f"Товары в заказе: {', '.join([item.product.name for item in order.items.all()])}, Общая сумма: {order.total_amount}"
        message = f"Ваш заказ №{order.id} успешно подтвержден. Данные заказа: {details}"
        recipient = order.contact.email
        send_mail(subject, message, 'no-reply@example.com', [recipient])

    @extend_schema(
        responses={201: OrderSerializer}
    )
    def create_from_cart(self, request):
        """Создание заказа на основе корзины"""
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response({'error': 'Корзина пуста'}, status=status.HTTP_400_BAD_REQUEST)

        contact_id = request.data.get('contact_id')
        try:
            contact = Contact.objects.get(id=contact_id, user=request.user)
        except Contact.DoesNotExist:
            return Response({'error': 'Контакт не найден'}, status=status.HTTP_404_NOT_FOUND)

        # Создаем заказ
        order = Order.objects.create(user=request.user, contact=contact, status='new')

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

        # Отправляем письмо с подтверждением заказа
        self.send_order_confirmation_email(order)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: CartItemSerializer(many=True)}
    )
    def get(self, request):
        """Получение текущей корзины пользователя"""
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={201: None}
    )
    def post(self, request):
        """Добавление товара в корзину"""
        user = request.user
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        product = get_object_or_404(Product, id=product_id)

        cart, _ = Cart.objects.get_or_create(user=user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += int(quantity)
        else:
            cart_item.quantity = int(quantity)
        cart_item.save()

        return Response({"message": "Продукт успешно добавлен в корзину."}, status=status.HTTP_201_CREATED)


class CartItemUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: None}
    )
    def patch(self, request, pk):
        """Обновление количества товара в корзине"""
        cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
        quantity = request.data.get('quantity')
        if quantity is None or int(quantity) <= 0:
            return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = quantity
        cart_item.save()

        return Response({'message': 'Item quantity updated'}, status=status.HTTP_200_OK)

    @extend_schema(
        responses={204: None}
    )
    def delete(self, request, pk):
        """Удаление товара из корзины"""
        cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
        cart_item.delete()
        return Response({'message': 'Item removed from cart'}, status=status.HTTP_204_NO_CONTENT)


class RemoveFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: None}
    )
    def delete(self, request, item_id):
        user = request.user
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=user)
        cart_item.delete()
        return Response({"message": "Продукт успешно удален из корзины."}, status=status.HTTP_200_OK)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: OrderSerializer}
    )
    def get(self, request, pk):
        """Получение информации о заказе"""
        order = get_object_or_404(Order, pk=pk, user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: AddressSerializer(many=True)}
    )
    def get_queryset(self):
        # Возвращаем только адреса текущего пользователя
        return self.queryset.filter(user=self.request.user)

    @extend_schema(
        responses={201: AddressSerializer}
    )
    def perform_create(self, serializer):
        # Устанавливаем текущего пользователя как владельца адреса
        serializer.save(user=self.request.user)

    @extend_schema(
        responses={204: None}
    )
    def destroy(self, request, *args, **kwargs):
        # Проверяем, что адрес принадлежит текущему пользователю
        address = self.get_object()
        if address.user != request.user:
            return Response({"error": "You cannot delete this address."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
