import yaml
from celery import shared_task
from products.models import Category, Product
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import os


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


@shared_task
def create_product_thumbnail(image_path):
    """Задача для создания миниатюр изображений товаров"""
    try:
        img = Image.open(image_path)
        img.thumbnail((100, 100))  # Миниатюра 100x100

        # Сохраняем миниатюру в память
        thumb_io = BytesIO()
        img.save(thumb_io, img.format)
        thumb_io.seek(0)

        # Создаем временный файл
        image_name = os.path.basename(image_path)
        new_image = InMemoryUploadedFile(
            thumb_io, None, image_name, 'image/jpeg', thumb_io.getbuffer().nbytes, None
        )

        return new_image
    except Exception as e:
        print(f"Error in creating thumbnail: {e}")
        return None
