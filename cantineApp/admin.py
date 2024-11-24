# cantineApp/admin.py

from django.contrib import admin
from .models import Product, Sale, Expense, Bill, BillItem, Stock, Accounting

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'image')
    search_fields = ('name',)

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity')
    search_fields = ('product__name',)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'amount', 'created_at')
    search_fields = ('description',)
    list_filter = ('created_at',)

@admin.register(Accounting)
class AccountingAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_sales', 'total_expenses', 'net_accounting')
    search_fields = ('date',)
    list_filter = ('date',)

admin.site.register(Sale)
admin.site.register(Bill)
admin.site.register(BillItem)
