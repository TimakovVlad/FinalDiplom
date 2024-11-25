import requests

BASE_URL = "http://127.0.0.1:8000/api/"
USERNAME = "admin"
PASSWORD = "admin"

def user_login(username=USERNAME, password=PASSWORD):
    url = f"{BASE_URL}users/login/"
    data = {"username": username, "password": password}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        token = response.json().get("access")  # JWT токен
        print("Токен получен успешно:", token)
        return token
    else:
        print("Ошибка при авторизации. Код ответа:", response.status_code)
        print("Ответ сервера:", response.text)
        return None

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
        "name": "Тестовый продукт",
        "description": "Описание тестового продукта",
        "category": 1,
        "supplier": "Тестовый поставщик",
        "price": "500.00",
        "quantity": 10,
        "parameters": {
            "color": "red",
            "size": "L"
        }
    }
    response = requests.post(BASE_URL + "products/products/", headers=headers, json=data)
    if response.status_code == 201:
        print("Продукт успешно создан:", response.json())
    else:
        print("Ошибка при создании продукта:", response.status_code, response.text)

if __name__ == "__main__":
    token = user_login('seregaP', "sergey288")
    if token:
        create_category(token, "Категория 1")
        create_product(token)
