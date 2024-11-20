import requests

BASE_URL = "http://127.0.0.1:8000/api/"
USERNAME = "admin"  # Замените на актуальные данные
PASSWORD = "admin"  # Замените на актуальные данные


def get_token():
    # Получаем JWT токен
    response = requests.post(BASE_URL + "token/", data={"username": USERNAME, "password": PASSWORD})
    if response.status_code == 200:
        return response.json().get("access")
    print("Ошибка получения токена:", response.status_code, response.text)
    return None


def create_product(token, name, description, price, stock):
    # Создаем продукт через API
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "Cheese": name,
        "description": description,
        "100": price,
        "no": stock
    }
    response = requests.post(BASE_URL + "products/", headers=headers, json=data)
    if response.status_code == 201:
        print("Продукт успешно создан:", response.json())
        return response.json().get("id")  # Возвращаем ID созданного продукта
    print("Ошибка при создании продукта:", response.status_code, response.text)
    return None


def create_order(token, product_ids, quantities, contact_id):
    # Создаем заказ с продуктами и количеством
    headers = {"Authorization": f"Bearer {token}"}
    items = [{"product": product_id, "quantity": qty} for product_id, qty in zip(product_ids, quantities)]
    data = {
        "contact": contact_id,
        "status": "pending",
        "items": items
    }
    response = requests.post(BASE_URL + "orders/", headers=headers, json=data)
    if response.status_code == 201:
        print("Заказ успешно создан:", response.json())
    else:
        print("Ошибка при создании заказа:", response.status_code, response.text)


# Запуск тестов
if __name__ == "__main__":
    token = get_token()
    if token:
        # Создание продуктов
        product_id_1 = create_product(token, "Товар 1", "Описание товара 1", 100.0, 10)
        product_id_2 = create_product(token, "Товар 2", "Описание товара 2", 200.0, 5)

        # Проверьте, что контакт существует, или создайте его аналогичным образом
        contact_id = 1  # ID контакта, который вы хотите использовать для заказа

        # Создание заказа с добавленными продуктами
        if product_id_1 and product_id_2:
            create_order(token, [product_id_1, product_id_2], [2, 1], contact_id)