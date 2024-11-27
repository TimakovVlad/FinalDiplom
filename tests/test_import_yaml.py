import pytest
from django.core.files.temp import NamedTemporaryFile
from products.models import Category, Product
from products.tasks import import_products_from_yaml

@pytest.mark.django_db
def test_import_products_from_yaml():
    # Создаём временный файл с тестовыми данными YAML
    yaml_content = """
    shop:
      name: "Test Shop"
      address: "123 Main St"

    categories:
      - name: "Electronics"
        products:
          - name: "Smartphone"
            description: "A high-end smartphone"
            price: 799.99
            quantity: 10
          - name: "Laptop"
            description: "A powerful laptop"
            price: 1199.99
            quantity: 5

      - name: "Books"
        products:
          - name: "Programming Book"
            description: "Learn Python programming"
            price: 29.99
            quantity: 50
    """
    with NamedTemporaryFile(delete=True, suffix=".yaml") as temp_file:
        temp_file.write(yaml_content.encode("utf-8"))
        temp_file.flush()

        # Передаём путь временного файла в задачу
        import_products_from_yaml(temp_file.name)

    # Проверяем, что категории созданы
    assert Category.objects.count() == 2
    assert Product.objects.count() == 3

    # Проверяем данные о категориях
    electronics = Category.objects.get(name="Electronics")
    books = Category.objects.get(name="Books")

    assert electronics.products.count() == 2
    assert books.products.count() == 1

    # Проверяем данные о продуктах
    smartphone = Product.objects.get(name="Smartphone")
    assert smartphone.description == "A high-end smartphone"
    assert float(smartphone.price) == 799.99
    assert smartphone.quantity == 10
