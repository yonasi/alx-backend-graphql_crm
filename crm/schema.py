import graphene
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db import transaction, IntegrityError
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter
from django.core.exceptions import ValidationError
import re

# Django Object Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ('id', 'name', 'email', 'phone', 'created_at')
        filterset_class = CustomerFilter
        interfaces = (graphene.relay.Node,)

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'stock')  # Only model fields
        filterset_class = ProductFilter
        interfaces = (graphene.relay.Node,)

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ('id', 'customer', 'products', 'order_date', 'total_amount')
        filterset_class = OrderFilter
        interfaces = (graphene.relay.Node,)

# Input Types for Mutations
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

# Input Types for Filters
class CustomerFilterInput(graphene.InputObjectType):
    name_icontains = graphene.String()
    email_icontains = graphene.String()
    created_at_gte = graphene.DateTime()
    created_at_lte = graphene.DateTime()
    phone_pattern = graphene.String()

class ProductFilterInput(graphene.InputObjectType):
    name_icontains = graphene.String()
    price_gte = graphene.Decimal()
    price_lte = graphene.Decimal()
    stock_gte = graphene.Int()
    stock_lte = graphene.Int()
    low_stock = graphene.Boolean()

class OrderFilterInput(graphene.InputObjectType):
    total_amount_gte = graphene.Decimal()
    total_amount_lte = graphene.Decimal()
    order_date_gte = graphene.DateTime()
    order_date_lte = graphene.DateTime()
    customer_name = graphene.String()
    product_name = graphene.String()
    product_id = graphene.ID()

# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        try:
            if input.phone:
                phone_pattern = re.compile(r'^\+?\d{1,4}?[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}$')
                if not phone_pattern.match(input.phone):
                    raise ValidationError("Invalid phone format. Use formats like +1234567890 or 123-456-7890.")

            customer = Customer(name=input.name, email=input.email, phone=input.phone)
            customer.full_clean()
            customer.save()
            return CreateCustomer(customer=customer, message="Customer created successfully")
        except IntegrityError:
            raise ValidationError("Email already exists")
        except ValidationError as e:
            raise ValidationError(str(e))

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        customers = []
        errors = []

        with transaction.atomic():
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

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        try:
            product = Product(name=input.name, price=input.price, stock=input.stock)
            product.full_clean()
            product.save()
            return CreateProduct(product=product)
        except ValidationError as e:
            raise ValidationError(str(e))

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            raise ValidationError(f"Customer with ID {input.customer_id} does not exist")

        if not input.product_ids:
            raise ValidationError("At least one product must be selected")

        products = []
        for product_id in input.product_ids:
            try:
                product = Product.objects.get(id=product_id)
                products.append(product)
            except Product.DoesNotExist:
                raise ValidationError(f"Product with ID {product_id} does not exist")

        order = Order(customer=customer)
        order.save()
        order.products.set(products)
        order.save()
        return CreateOrder(order=order)

# Query Class with Filtering
class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter, order_by=graphene.String())
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter, order_by=graphene.String())
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter, order_by=graphene.String())

    def resolve_all_customers(self, info, **kwargs):
        queryset = Customer.objects.all()
        order_by = kwargs.get('order_by')
        if order_by:
            queryset = queryset.order_by(order_by)
        return queryset

    def resolve_all_products(self, info, **kwargs):
        queryset = Product.objects.all()
        order_by = kwargs.get('order_by')
        if order_by:
            queryset = queryset.order_by(order_by)
        return queryset

    def resolve_all_orders(self, info, **kwargs):
        queryset = Order.objects.all()
        order_by = kwargs.get('order_by')
        if order_by:
            queryset = queryset.order_by(order_by)
        return queryset

# Mutation Class
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()