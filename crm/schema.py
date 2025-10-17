# crm/schema.py
import graphene
from graphene_django import DjangoObjectType
from .models import Customer  # ✅ make sure Customer model exists in crm/models.py


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
