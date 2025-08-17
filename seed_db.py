import os
import django
from django.utils import timezone
from decimal import Decimal

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

# Now import models after Django is set up
from crm.models import Customer, Product, Order

def seed_db():
    # Clear existing data
    Customer.objects.all().delete()
    Product.objects.all().delete()
    Order.objects.all().delete()

    # Create customers
    customers = [
        Customer(name="Alice", email="alice@example.com", phone="+1234567890"),
        Customer(name="Bob", email="bob@example.com", phone="123-456-7890"),
        Customer(name="Carol", email="carol@example.com"),
    ]
    Customer.objects.bulk_create(customers)

    # Create products
    products = [
        Product(name="Laptop", price=Decimal('999.99'), stock=10),
        Product(name="Phone", price=Decimal('499.99'), stock=20),
    ]
    Product.objects.bulk_create(products)

    # Create an order
    order = Order(customer=customers[0], order_date=timezone.now())
    order.save()
    order.products.set(products)
    order.save()

    print("Database seeded successfully!")

if __name__ == "__main__":
    seed_db()