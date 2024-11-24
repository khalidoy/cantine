# cantineApp/models.py

from django.db import models
from django.utils import timezone
from decimal import Decimal  # Import Decimal for precise arithmetic

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    def __str__(self):
        return self.name

class Stock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='stock')
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - Stock: {self.quantity}"

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)  # Updated field

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class Expense(models.Model):
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.description

class Bill(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"Bill {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class BillItem(models.Model):
    bill = models.ForeignKey(Bill, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def save(self, *args, **kwargs):
        self.subtotal = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class Accounting(models.Model):
    date = models.DateField(unique=True)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2)
    total_expenses = models.DecimalField(max_digits=10, decimal_places=2)
    net_accounting = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Accounting for {self.date}"
