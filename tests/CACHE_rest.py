import requests

# URL для логина
BASE_URL = "http://127.0.0.1:8000/api/"
login_url = "http://127.0.0.1:8000/api/users/login/"
login_data = {
    "username": "admin",
    "password": "admin",
}

# Отправляем запрос на авторизацию
login_response = requests.post(login_url, data=login_data)

# Проверяем, если авторизация успешна и получаем токен
if login_response.status_code == 200:
    token = login_response.json().get('access')  # Обычно токен хранится в поле 'access'
    print("Токен получен:", token)
else:
    print("Ошибка авторизации", login_response.status_code, login_response.text)

def create_category(token, name):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "name": name
    }
    response = requests.post(BASE_URL + "products/categories/", headers=headers, json=data)
    if response.status_code == 201:
        print("Категория успешно создана:", response.json())
    else:
        print("Ошибка при создании категории:", response.status_code, response.text)

def create_product(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "name": "Тестовый продукт3",
        "description": "Описание тестового продукта2",
        "category": 3,
        "supplier": "Тестовый поставщик2",
        "price": "500.00",
        "quantity": 10,
        "parameters": {
            "color": "red",
            "size": "L"
        }
    }
    response = requests.post(BASE_URL + "products/", headers=headers, json=data)
    if response.status_code == 201:
        print("Продукт успешно создан:", response.json())
    else:
        print("Ошибка при создании продукта:", response.status_code, response.text)

if token:
    create_category(token, "Тестовая категория3")
    create_product(token)

# [10/Dec/2024 17:00:55] "POST /api/products/categories/ HTTP/1.1" 400 52
# [10/Dec/2024 17:00:55] "POST /api/products/ HTTP/1.1" 201 307
# Time taken to fetch products: 0.0234 seconds
# [10/Dec/2024 17:01:55] "POST /api/users/login/ HTTP/1.1" 200 483
# [10/Dec/2024 17:01:55] "POST /api/products/categories/ HTTP/1.1" 201 54
# Time taken to fetch products: 0.0131 seconds
# [10/Dec/2024 17:01:55] "POST /api/products/ HTTP/1.1" 201 321