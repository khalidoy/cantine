# cantineApp/admin.py

from django.contrib import admin
from .models import Product, Stock, Sale, Expense, Bill, BillItem, Accounting

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity')
    search_fields = ('product__name',)

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('product__name',)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('description',)

class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 1

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_name', 'total', 'is_credit', 'created_at', 'paid_at')
    list_filter = ('is_credit', 'created_at', 'paid_at')
    search_fields = ('client_name',)
    inlines = [BillItemInline]

@admin.register(Accounting)
class AccountingAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_sales', 'total_expenses', 'net_accounting')
    list_filter = ('date',)
