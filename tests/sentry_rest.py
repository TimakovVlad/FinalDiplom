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


if token:
    # URL для вызова API, который вызывает исключение (или ваш нужный API)
    api_url = "http://127.0.0.1:8000/api/products/error/trigger-error/"

    # Заголовки с токеном для авторизации
    headers = {
        "Authorization": f"Bearer {token}",
    }

    # Отправляем запрос с авторизацией
    api_response = requests.get(api_url, headers=headers)

    # Выводим результат
    print(api_response.status_code)
    print(api_response.json())
