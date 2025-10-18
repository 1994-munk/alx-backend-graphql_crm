# schema.py
from crm.schema import Query as CRMQuery,CRMMutation  # ✅ import Query from crm
import graphene  # Graphene is the library that handles GraphQL in Django
from graphene_django import DjangoObjectType
from crm.models import Customer, Product, Order
from django.core.exceptions import ValidationError
from django.db import transaction

# 🧠 Define a simple Query class
class Query(graphene.ObjectType):
    # Create a field named 'hello' that returns a String
    hello = graphene.String()

# Combine all queries from crm and other apps here
class Query(CRMQuery, graphene.ObjectType):
    pass

class Mutation(CRMMutation, graphene.ObjectType):
    pass

    # Define what happens when someone queries the 'hello' field
    def resolve_hello(root, info):
        # This function is called whenever someone requests { hello }
        return "Hello, GraphQL!"

# 🔗 Combine all queries into a schema
schema = graphene.Schema(query=Query ,mutation=Mutation)

# 🧱 GraphQL Object Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"


# 💌 Create Customer Mutation
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists.")
        customer = Customer.objects.create(name=name, email=email, phone=phone)
        return CreateCustomer(customer=customer, message="Customer created successfully!")

# ✅ Define input type properly
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

# ✅ Define mutation using the class name, not instance
class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        customers = graphene.NonNull(graphene.List(graphene.NonNull(CustomerInput)))

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, customers):
        created = []
        errors = []

        for c in customers:
            try:
                customer = Customer.objects.create(
                    name=c.name,
                    email=c.email,
                    phone=c.phone,
                )
                created.append(customer)
            except Exception as e:
                errors.append(str(e))

        return BulkCreateCustomers(customers=created, errors=errors)


# ✅ Add to your root schema
class Mutation(graphene.ObjectType):
    bulk_create_customers = BulkCreateCustomers.Field()


schema = graphene.Schema(mutation=Mutation)

                

# 💰 Create Product Mutation
class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=False, default_value=0)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock):
        if price <= 0:
            raise Exception("Price must be positive.")
        if stock < 0:
            raise Exception("Stock cannot be negative.")
        product = Product.objects.create(name=name, price=price, stock=stock)
        return CreateProduct(product=product)


# 🛒 Create Order Mutation
class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID")

        products = Product.objects.filter(id__in=product_ids)
        if not products.exists():
            raise Exception("Invalid product IDs")

        order = Order.objects.create(customer=customer)
        order.products.set(products)
        order.save()

        return CreateOrder(order=order)


# 📋 CRM Query + Mutation root
class Query(graphene.ObjectType):
    all_customers = graphene.List(CustomerType)
    all_products = graphene.List(ProductType)
    all_orders = graphene.List(OrderType)

    def resolve_all_customers(root, info):
        return Customer.objects.all()

    def resolve_all_products(root, info):
        return Product.objects.all()

    def resolve_all_orders(root, info):
        return Order.objects.all()


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()