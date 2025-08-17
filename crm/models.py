from django.db import models
import re

class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Added for filtering

    def clean(self):
        if self.phone:
            phone_pattern = re.compile(r'^\+?\d{1,4}?[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}$')
            if not phone_pattern.match(self.phone):
                raise ValueError("Invalid phone format. Use formats like +1234567890 or 123-456-7890.")

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)

    def clean(self):
        if self.price <= 0:
            raise ValueError("Price must be positive.")
        if self.stock < 0:
            raise ValueError("Stock cannot be negative.")

    def __str__(self):
        return self.name

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.products.exists():
            self.total_amount = sum(product.price for product in self.products.all())
            super().save(update_fields=['total_amount'])

    def __str__(self):
        return f"Order {self.id} by {self.customer.name}"