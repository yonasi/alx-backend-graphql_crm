import graphene
from graphene_django.types import DjangoObjectType
from django.db import transaction, IntegrityError
from .models import Customer, Product, Order
from django.core.exceptions import ValidationError
import re

# Django Object Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ('id', 'name', 'email', 'phone')

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'stock')

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ('id', 'customer', 'products', 'order_date', 'total_amount')

# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int(required=False, default_value=0)

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime(required=False)

# CreateCustomer Mutation
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        try:
            # Validate phone format
            if input.phone:
                phone_pattern = re.compile(r'^\+?\d{1,4}?[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}$')
                if not phone_pattern.match(input.phone):
                    raise ValidationError("Invalid phone format. Use formats like +1234567890 or 123-456-7890.")

            customer = Customer(name=input.name, email=input.email, phone=input.phone)
            customer.full_clean()  # Run model validation
            customer.save()
            return CreateCustomer(customer=customer, message="Customer created successfully")
        except IntegrityError:
            raise ValidationError("Email already exists")
        except ValidationError as e:
            raise ValidationError(str(e))

# BulkCreateCustomers Mutation
class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        customers = []
        errors = []

        with transaction.atomic():  # Ensure atomic transaction
            for i, customer_input in enumerate(input):
                try:
                    if customer_input.phone:
                        phone_pattern = re.compile(r'^\+?\d{1,4}?[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}$')
                        if not phone_pattern.match(customer_input.phone):
                            errors.append(f"Customer {i+1}: Invalid phone format")
                            continue

                    customer = Customer(
                        name=customer_input.name,
                        email=customer_input.email,
                        phone=customer_input.phone
                    )
                    customer.full_clean()
                    customer.save()
                    customers.append(customer)
                except IntegrityError:
                    errors.append(f"Customer {i+1}: Email {customer_input.email} already exists")
                except ValidationError as e:
                    errors.append(f"Customer {i+1}: {str(e)}")

        return BulkCreateCustomers(customers=customers, errors=errors)

# CreateProduct Mutation
class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        try:
            product = Product(name=input.name, price=input.price, stock=input.stock)
            product.full_clean()  # Run model validation
            product.save()
            return CreateProduct(product=product)
        except ValidationError as e:
            raise ValidationError(str(e))

# CreateOrder Mutation
class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        try:
            # Validate customer
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            raise ValidationError(f"Customer with ID {input.customer_id} does not exist")

        # Validate products
        if not input.product_ids:
            raise ValidationError("At least one product must be selected")

        products = []
        for product_id in input.product_ids:
            try:
                product = Product.objects.get(id=product_id)
                products.append(product)
            except Product.DoesNotExist:
                raise ValidationError(f"Product with ID {product_id} does not exist")

        # Create order
        order = Order(customer=customer)
        order.save()
        order.products.set(products)  # Associate products
        order.save()  # Trigger total_amount calculation

        return CreateOrder(order=order)

# Query (for completeness)
class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(self, info):
        return Customer.objects.all()

    def resolve_products(self, info):
        return Product.objects.all()

    def resolve_orders(self, info):
        return Order.objects.all()

# Mutation Class
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()