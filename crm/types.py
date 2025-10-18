# crm/types.py

import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order


# 🎯 GraphQL Type for Customer model
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at")


# 🎯 GraphQL Type for Product model
class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")


# 🎯 GraphQL Type for Order model
class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")
