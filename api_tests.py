import requests

BASE_URL = "http://127.0.0.1:8000/api"
USERNAME = "admin"
PASSWORD = "admin"


def get_token(username=USERNAME, password=PASSWORD):
    # Получаем JWT токен
    response = requests.post(BASE_URL + "/token/", data={"username": username, "password": password})
    if response.status_code == 200:
        return response.json().get("access")
    print("Ошибка получения токена:", response.status_code, response.text)
    return None


# def create_product(token, name, description, price, stock):
#     # Создаем продукт через API
#     headers = {"Authorization": f"Bearer {token}"}
#     data = {
#         "name": name,
#         "description": description,
#         "price": price,
#         "stock": stock
#     }
#     response = requests.post(BASE_URL + "/products/", headers=headers, json=data)
#     if response.status_code == 201:
#         print("Продукт успешно создан:", response.json())
#         return response.json().get("id")  # Возвращаем ID созданного продукта
#     print("Ошибка при создании продукта:", response.status_code, response.text)
#     return None
#
#
# def create_order(token, product_ids, quantities, contact_id):
#     # Создаем заказ с продуктами и количеством
#     headers = {"Authorization": f"Bearer {token}"}
#     items = [{"product": product_id, "quantity": qty} for product_id, qty in zip(product_ids, quantities)]
#     data = {
#         "contact": contact_id,
#         "status": "pending",
#         "items": items
#     }
#     response = requests.post(BASE_URL + "/orders/", headers=headers, json=data)
#     if response.status_code == 201:
#         print("Заказ успешно создан:", response.json())
#     else:
#         print("Ошибка при создании заказа:", response.status_code, response.text)
#
#
# # Запуск тестов
# if __name__ == "__main__":
#     token = get_token()
#     if token:
#         # Создание продуктов
#         product_id_1 = create_product(token, "Товар 1", "Описание товара 1", 100.0, 10)
#         product_id_2 = create_product(token, "Товар 2", "Описание товара 2", 200.0, 5)
#
#         # Проверьте, что контакт существует, или создайте его аналогичным образом
#         contact_id = 1  # ID контакта, который вы хотите использовать для заказа
#
#         # Создание заказа с добавленными продуктами
#         if product_id_1 and product_id_2:
#             create_order(token, [product_id_1, product_id_2], [2, 1], contact_id)



def add_item_to_cart(token, product_id, quantity):
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "product_id": product_id,
        "quantity": quantity
    }
    response = requests.post(BASE_URL + "/cart/", headers=headers, json=data)
    if response.status_code == 201:
        print("Товар успешно добавлен в корзину:", response.json())
    else:
        print("Ошибка при добавлении товара в корзину:", response.status_code, response.text)

def create_order_from_cart(client, user, product, contact):
    client.force_authenticate(user=user)

    # Добавление товара в корзину
    response = client.post('/api/cart/', {'product_id': product.id, 'quantity': 2})
    assert response.status_code == 201

    # Создание заказа из корзины
    response = client.post('/api/orders/create-from-cart/', {'contact_id': contact.id})
    assert response.status_code == 201

    # Проверяем, что корзина пуста
    response = client.get('/api/cart/')
    assert len(response.data['items']) == 0

    # Проверяем, что заказ создан
    response = client.get('/api/orders/')
    assert len(response.data) == 1
    assert response.data[0]['status'] == 'pending'


def test_user_registration(username, email, password):
    """Тест для регистрации нового пользователя."""
    url = f"{BASE_URL}/register/"
    user_data = {
        "username": username,
        "email": email,
        "password": password
    }

    response = requests.post(url, data=user_data)

    if response.status_code == 201:
        print("Пользователь успешно зарегистрирован!")
        print("Ответ сервера:", response.json())
    else:
        print("Ошибка при регистрации пользователя.")
        print("Код ответа:", response.status_code)
        print("Ответ сервера:", response.json())


if __name__ == "__main__":
    test_user_registration("seregaP", "sp96@ya.ru", "sergey288")
    # token = get_token("seregaP", "sergey288")
    # if token:
    #     # Добавление товара в корзину
    #     product_id = 1  # ID товара, который вы хотите добавить в корзину
    #     quantity = 2  # Количество товара, которое вы хотите добавить в корзину
    #     add_item_to_cart(token, product_id, quantity)
    #
    #     # Создание заказа из корзины
    #     contact_id = 1  # ID контакта, который вы хотите использовать для заказа
    #     create_order_from_cart(token, contact_id)