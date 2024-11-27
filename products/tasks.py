import yaml
from celery import shared_task
from products.models import Category, Product


@shared_task
def import_products_from_yaml(yaml_path):
    """Асинхронная задача для импорта товаров из YAML."""
    with open(yaml_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    for category_data in data.get('categories', []):
        # Создаём или получаем категорию
        category, _ = Category.objects.get_or_create(name=category_data['name'])

        # Добавляем товары в категорию
        for product_data in category_data.get('products', []):
            Product.objects.update_or_create(
                name=product_data['name'],
                defaults={
                    'description': product_data.get('description', ''),
                    'price': product_data['price'],
                    'quantity': product_data['quantity'],
                    'category': category
                }
            )
    return {"status": "success", "message": "Товары успешно импортированы"}
