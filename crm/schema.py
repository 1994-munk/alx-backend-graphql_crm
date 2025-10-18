# crm/schema.py
import graphene
import re
from graphene_django import DjangoObjectType
from .models import Customer , Product, Order # ✅ make sure Customer model exists in crm/models.py
from django.db import transaction
from django.utils import timezone
from graphene_django import DjangoObjectType


# Define how the Customer model is exposed to GraphQL
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")  


# Define your Query class for fetching customers
class Query(graphene.ObjectType):
    all_customers = graphene.List(CustomerType)

    # Resolver method for all_customers
    def resolve_all_customers(root, info):
        return Customer.objects.all()

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")

# =======================
# Input Types
# =======================

class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


# =======================
# CreateCustomer Mutation
# =======================

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input):
        errors = []

        # Validate email uniqueness
        if Customer.objects.filter(email=input.email).exists():
            errors.append("Email already exists.")

        # Validate phone format if provided
        if input.phone and not re.match(r"^(\+?\d{7,15}|(\d{3}-\d{3}-\d{4}))$", input.phone):
            errors.append("Invalid phone format. Use +1234567890 or 123-456-7890.")

        if errors:
            return CreateCustomer(errors=errors)

        # Create customer
        customer = Customer.objects.create(
            name=input.name,
            email=input.email,
            phone=input.phone
        )

        return CreateCustomer(customer=customer, message="Customer created successfully.")


# =======================
# BulkCreateCustomers
# =======================

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input):
        created_customers = []
        errors = []

        with transaction.atomic():
            for data in input:
                # Validate email
                if Customer.objects.filter(email=data.email).exists():
                    errors.append(f"Email {data.email} already exists.")
                    continue

                # Validate phone
                if data.phone and not re.match(r"^(\+?\d{7,15}|(\d{3}-\d{3}-\d{4}))$", data.phone):
                    errors.append(f"Invalid phone for {data.name}.")
                    continue

                # Create customer
                customer = Customer(name=data.name, email=data.email, phone=data.phone)
                customer.save()
                created_customers.append(customer)

        return BulkCreateCustomers(customers=created_customers, errors=errors)


# =======================
# CreateProduct
# =======================

class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(default_value=0)

    product = graphene.Field(ProductType)
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, name, price, stock):
        errors = []

        if price <= 0:
            errors.append("Price must be positive.")
        if stock < 0:
            errors.append("Stock cannot be negative.")

        if errors:
            return CreateProduct(errors=errors)

        product = Product.objects.create(name=name, price=price, stock=stock)
        return CreateProduct(product=product)


# =======================
# CreateOrder
# =======================

class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime(default_value=timezone.now)

    order = graphene.Field(OrderType)
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, customer_id, product_ids, order_date):
        errors = []

        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            errors.append("Invalid customer ID.")
            return CreateOrder(errors=errors)

        if not product_ids:
            errors.append("At least one product must be selected.")
            return CreateOrder(errors=errors)

        products = Product.objects.filter(pk__in=product_ids)
        if not products.exists():
            errors.append("Invalid product IDs.")
            return CreateOrder(errors=errors)

        total_amount = sum(p.price for p in products)

        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            order_date=order_date
        )
        order.products.set(products)

        return CreateOrder(order=order)


# =======================
# Root Mutation Class
# =======================

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()


# =======================
# Root Query Class
# =======================

class Query(graphene.ObjectType):
    all_customers = graphene.List(CustomerType)
    all_products = graphene.List(ProductType)
    all_orders = graphene.List(OrderType)

    def resolve_all_customers(root, info):
        return Customer.objects.all()

    def resolve_all_products(root, info):
        return Product.objects.all()
    def resolve_all_orders(root, info):
        return Order.objects.select_related('customer').prefetch_related('products').all()
    
  # This is just a temporary placeholder for your CRM mutations
class CRMMutation(graphene.ObjectType):
    pass  