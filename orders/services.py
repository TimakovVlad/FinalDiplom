from django.db import transaction


@transaction.atomic
def create_order_from_cart(user, contact):
    cart = Cart.objects.get(user=user)  # Получаем корзину пользователя
    if not cart.items.exists():
        raise ValueError("Корзина пуста!")

    # Создаем заказ
    order = Order.objects.create(
        user=user,
        contact=contact,
        status='pending',
    )

    # Переносим товары из корзины в заказ
    for cart_item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price=cart_item.product.price  # Берем актуальную цену товара
        )

    # Рассчитываем общую сумму заказа
    order.calculate_total_amount()

    # Очищаем корзину
    cart.items.all().delete()

    return order
