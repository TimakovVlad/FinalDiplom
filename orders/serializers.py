from rest_framework import serializers
from .models import Order, OrderItem, Cart, CartItem, Address

class OrderItemSerializer(serializers.ModelSerializer):
    # Сериализатор для единицы товара в заказе
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    # Вложенный сериализатор для связи с OrderItem
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'created_at', 'updated_at', 'items']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Создание заказа вместе с вложенными OrderItem
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items']
        read_only_fields = ['user']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'title', 'address_line', 'city', 'postal_code', 'country', 'created_at']
        read_only_fields = ['id', 'created_at']
