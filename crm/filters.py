from django_filters import rest_framework as filters
from .models import Customer, Product, Order
import re

class CustomerFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    email = filters.CharFilter(field_name='email', lookup_expr='icontains')
    created_at_gte = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_lte = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    phone_pattern = filters.CharFilter(method='filter_phone_pattern')

    class Meta:
        model = Customer
        fields = ['name', 'email', 'created_at_gte', 'created_at_lte', 'phone_pattern']

    def filter_phone_pattern(self, queryset, name, value):
        if value:
            pattern = f'^{re.escape(value)}'
            return queryset.filter(phone__regex=pattern)
        return queryset

class ProductFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    price_gte = filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_lte = filters.NumberFilter(field_name='price', lookup_expr='lte')
    stock_gte = filters.NumberFilter(field_name='stock', lookup_expr='gte')
    stock_lte = filters.NumberFilter(field_name='stock', lookup_expr='lte')
    low_stock = filters.BooleanFilter(method='filter_low_stock')

    class Meta:
        model = Product
        fields = ['name', 'price_gte', 'price_lte', 'stock_gte', 'stock_lte', 'low_stock']

    def filter_low_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__lt=10)
        return queryset

class OrderFilter(filters.FilterSet):
    total_amount_gte = filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    total_amount_lte = filters.NumberFilter(field_name='total_amount', lookup_expr='lte')
    order_date_gte = filters.DateTimeFilter(field_name='order_date', lookup_expr='gte')
    order_date_lte = filters.DateTimeFilter(field_name='order_date', lookup_expr='lte')
    customer_name = filters.CharFilter(method='filter_customer_name')
    product_name = filters.CharFilter(method='filter_product_name')
    product_id = filters.NumberFilter(method='filter_product_id')

    class Meta:
        model = Order
        fields = ['total_amount_gte', 'total_amount_lte', 'order_date_gte', 'order_date_lte', 'customer_name', 'product_name', 'product_id']

    def filter_customer_name(self, queryset, name, value):
        return queryset.filter(customer__name__icontains=value)

    def filter_product_name(self, queryset, name, value):
        return queryset.filter(products__name__icontains=value)

    def filter_product_id(self, queryset, name, value):
        return queryset.filter(products__id=value)