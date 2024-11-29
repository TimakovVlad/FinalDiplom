from django.conf import settings
from django.db import models
from products.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id} for {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('basket', 'Статус корзины'),
        ('new', 'Новый'),
        ('confirmed', 'Подтвержден'),
        ('assembled', 'Собран'),
        ('sent', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('canceled', 'Отменен'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)                                        # Автоматическое обновление при каждом изменении
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    contact = models.ForeignKey('Contact', on_delete=models.SET_NULL, null=True)

    def calculate_total_amount(self):
        self.total_amount = sum(item.price * item.quantity for item in self.items.all())
        self.save()

    def change_status(self, new_status):
        """
        Меняет статус заказа, если переход допустим.
        """
        allowed_transitions = {
            'basket': ['new'],
            'new': ['confirmed', 'canceled'],
            'confirmed': ['assembled', 'canceled'],
            'assembled': ['sent', 'canceled'],
            'sent': ['delivered'],
            'delivered': [],
            'canceled': [],
        }
        if new_status not in allowed_transitions[self.status]:
            raise ValueError(f"Переход из статуса {self.status} в {new_status} невозможен.")

        self.status = new_status
        self.save()

    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')    # Cвязь с моделью Order
    product = models.ForeignKey(Product, on_delete=models.CASCADE)                      # Cвязь с моделью Product
    quantity = models.PositiveIntegerField()                                            # Количество товара в заказе
    price = models.DecimalField(max_digits=10, decimal_places=2)                        # Цена товара на момент добавления в заказ

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class Contact(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contacts')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    title = models.CharField(max_length=255, verbose_name="Название адреса")
    address_line = models.TextField(verbose_name="Адрес")
    city = models.CharField(max_length=100, verbose_name="Город")
    postal_code = models.CharField(max_length=20, verbose_name="Почтовый индекс")
    country = models.CharField(max_length=100, verbose_name="Страна")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"

    def __str__(self):
        return f"{self.title} ({self.user.username})"
