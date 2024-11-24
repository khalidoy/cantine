# cantineApp/forms.py

from django import forms
from .models import Product, Sale, Expense, Stock

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product', 'quantity', 'total_price']  # Exclude 'created_at'

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['description', 'amount']

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }
