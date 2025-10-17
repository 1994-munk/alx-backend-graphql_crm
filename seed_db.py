from crm.models import Customer, Product
from django.utils import timezone

# 🌸 Seed Customers
Customer.objects.create(name="Alice", email="alice@example.com", phone="+123456789")
Customer.objects.create(name="Bob", email="bob@example.com", phone="987-654-321")

# 🌸 Seed Products
Product.objects.create(name="Laptop", price=999.99, stock=10)
Product.objects.create(name="Phone", price=499.99, stock=15)

print("✅ Database seeded successfully!")
