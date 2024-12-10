from celery import shared_task
from easy_thumbnails.files import get_thumbnailer
from retail_automation.settings import THUMBNAIL_ALIASES


@shared_task
def generate_thumbnail(image_path, size='small'):
    """
    Асинхронная задача для создания миниатюры.
    :param image_path: путь к изображению
    :param size: размер миниатюры ('small', 'medium', 'large')
    """
    from django.core.files.storage import default_storage
    from django.core.files.images import ImageFile

    # Получаем объект изображения по пути
    with default_storage.open(image_path, 'rb') as f:
        image = ImageFile(f)

    # Создаём миниатюру с помощью easy-thumbnails
    thumbnailer = get_thumbnailer(image)
    thumbnail = thumbnailer.get_thumbnail(THUMBNAIL_ALIASES[''][size])

    return thumbnail.url  # Возвращаем URL миниатюры
