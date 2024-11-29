from celery import shared_task
from .models import Order
from django.utils.timezone import now
import logging

logger = logging.getLogger(__name__)

@shared_task
def check_pending_orders():
    """Проверяет заказы со статусом 'ожидание' и обновляет их."""
    orders = Order.objects.filter(status='pending', created_at__lt=now())
    for order in orders:
        # Обновляем статус (пример)
        order.status = 'canceled'
        order.save()
        logger.info(f"Order {order.id} canceled due to timeout.")
    return f"{orders.count()} orders processed."
