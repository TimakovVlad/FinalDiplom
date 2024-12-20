# Retail Automation

Проект для автоматизации работы с заказами, корзинами и пользователями в интернет-магазине. Включает в себя создание, обновление и изменение статусов заказов, управление корзинами, а также изменение паролей пользователей через API.

## Описание

Проект представляет собой Django REST API для интернет-магазина. Пользователи могут:

- Создавать заказы на основе содержимого корзины.
- Просматривать детали заказов.
- Изменять статус заказов (например, "подтвержден", "собран", "отправлен", "доставлен").
- Обновлять информацию о своих адресах и корзинах.
- Изменять свой пароль через API.

## Стек технологий

- **Python 3.10**
- **Django 5.1.3**
- **Django REST Framework 3.14**
- **pytest** для тестирования

## Установка

1. Клонировать репозиторий:

   ```bash
   git clone <repository_url>
   cd retail_automation
   ```

2. Установить зависимости:
   ```bash
    pip install -r requirements.txt
   ```

3. Выполнить миграции базы данных:
    ```bash
    python manage.py migrate
    ```

4. Запустить сервер:
    ```bash
    python manage.py runserver
    ```

## API эндпоинты

### Заказы

- **POST** `/api/orders/create-from-cart/`  
  Создание заказа на основе содержимого корзины. Возвращает ID нового заказа.

- **GET** `/api/orders/orders/{order_id}/`  
  Получение информации о заказе по его ID. Возвращает текущий статус и данные заказа.

- **PATCH** `/api/orders/orders/{order_id}/`  
  Обновление данных заказа, включая статус. Статус может быть обновлён в пределах допустимых значений, таких как "new", "confirmed", "assembled", "sent", "delivered".

- **PATCH** `/api/orders/orders/{order_id}/change-status/`  
  Специальный endpoint для изменения статуса заказа. Обновляет статус заказа, если он не завершён (например, если заказ в статусах "confirmed", "delivered", "canceled", то изменить статус нельзя).

### Корзина

- **GET** `/api/cart/`  
  Получение содержимого корзины текущего пользователя. Возвращает список всех товаров в корзине.

- **POST** `/api/cart/`  
  Добавление товара в корзину. Требует указания ID товара и количества.

- **DELETE** `/api/cart/{item_id}/`  
  Удаление товара из корзины по его ID.

### Продукты

- **GET** `/api/products/`  
  Получение списка всех доступных продуктов. Возвращает информацию о каждом продукте, включая название, описание и цену.

- **POST** `/api/products/`  
  Добавление нового продукта в систему. Требует прав администратора.

- **GET** `/api/products/{product_id}/`  
  Получение информации о конкретном продукте по его ID. Возвращает полные данные о продукте, включая название, описание, цену и другие характеристики.

- **PATCH** `/api/products/{product_id}/`  
  Обновление данных продукта. Можно изменить цену, описание или другие атрибуты продукта.

- **DELETE** `/api/products/{product_id}/`  
  Удаление продукта из системы. Требует прав администратора.

### Пользователи

- **POST** `/api/users/register/`  
  Регистрация нового пользователя. Принимает имя пользователя, email и пароль.

- **POST** `/api/users/login/`  
  Аутентификация пользователя. Принимает имя пользователя и пароль, возвращает токен для дальнейшей аутентификации.

- **PATCH** `/api/users/change-password/`  
  Изменение пароля пользователя. Требует старый и новый пароль.

Для более подробного описания API в проекте используются **drf-yasg**. Можно посмотреть документацию API в [Swagger UI](http://127.0.0.1:8000/api/docs/swagger/).

### Тестирование

Для тестирования API в проекте используются **pytest** и **pytest-django**. Все тесты можно запустить командой:
```bash
pytest
```

## Важные моменты

- Все API эндпоинты защищены аутентификацией, используется токен аутентификации.
- При создании заказа из корзины, корзина очищается.
- Статусы заказов могут быть изменены через специальный endpoint, и изменения статуса проверяются для соблюдения бизнес-логики (например, нельзя изменить статус завершенного заказа).