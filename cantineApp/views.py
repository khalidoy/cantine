# cantineApp/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from .models import Product, Bill, Expense, BillItem, Stock, Accounting
from .forms import ProductForm, StockForm, ExpenseForm
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.utils import timezone
from django.contrib import messages
from django.db.models import Sum, F, DecimalField, ExpressionWrapper, Q
from django.db.models.functions import Coalesce
from decimal import Decimal
import json
from datetime import datetime

def dashboard(request):
    products = Product.objects.all()
    bills = Bill.objects.order_by('-created_at')[:50]
    expenses = Expense.objects.order_by('-created_at')[:50]

    total_bills = Bill.objects.aggregate(total=Coalesce(Sum('total'), Decimal('0.00')))['total']
    total_expenses = Expense.objects.aggregate(total=Coalesce(Sum('amount'), Decimal('0.00')))['total']

    context = {
        'products': products,
        'bills': bills,
        'expenses': expenses,
        'total_bills': total_bills,
        'total_expenses': total_expenses,
    }
    return render(request, 'dashboard.html', context)

def caisse(request):
    products = Product.objects.all()
    return render(request, 'caisse.html', {'products': products})

@csrf_protect
def add_to_bill(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            is_credit = data.get('is_credit', False)
            client_name = data.get('client_name', '').strip()
            if not items:
                return JsonResponse({'error': 'No items provided'}, status=400)
            if is_credit and not client_name:
                return JsonResponse({'error': 'Client name is required for credit'}, status=400)
            bill = Bill.objects.create(total=Decimal('0.00'), is_credit=is_credit, client_name=client_name)
            total = Decimal('0.00')
            for item in items:
                product_id = item.get('product_id')
                quantity = int(item.get('quantity', 1))
                product = get_object_or_404(Product, id=product_id)
                stock = get_object_or_404(Stock, product=product)
                
                if stock.quantity < quantity:
                    return JsonResponse({'error': f'Not enough stock for {product.name}'}, status=400)
                
                stock.quantity -= quantity
                stock.save()
                
                subtotal = product.price * quantity
                BillItem.objects.create(
                    bill=bill,
                    product=product,
                    quantity=quantity,
                    subtotal=subtotal
                )
                total += subtotal
            
            bill.total = total
            bill.save()
            
            return JsonResponse({'bill_id': bill.id, 'total': str(bill.total)})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def view_bill(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    return render(request, 'bill.html', {'bill': bill})

@csrf_exempt
def bill_details(request, bill_id):
    if request.method == 'GET':
        try:
            bill = get_object_or_404(Bill, id=bill_id)
            items = bill.items.all().select_related('product')
            items_data = [
                {
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'subtotal': str(item.subtotal)
                }
                for item in items
            ]
            data = {
                'bill_id': bill.id,
                'created_at': bill.created_at.strftime('%Y-%m-%d %H:%M'),
                'total': str(bill.total),
                'items': items_data
            }
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

# Product CRUD Views
def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            Stock.objects.create(product=product, quantity=0)
            messages.success(request, 'Product added successfully.')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'products/product_form.html', {'form': form})

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/product_form.html', {'form': form})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('product_list')
    return render(request, 'products/product_confirm_delete.html', {'product': product})

# Stock CRUD Views
def stock_list(request):
    stocks = Stock.objects.select_related('product').all()
    return render(request, 'stock/stock_list.html', {'stocks': stocks})

def stock_create(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stock added successfully.')
            return redirect('stock_list')
    else:
        form = StockForm()
    return render(request, 'stock/stock_form.html', {'form': form})

def stock_update(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stock updated successfully.')
            return redirect('stock_list')
    else:
        form = StockForm(instance=stock)
    return render(request, 'stock/stock_form.html', {'form': form})

def stock_delete(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == 'POST':
        stock.delete()
        messages.success(request, 'Stock deleted successfully.')
        return redirect('stock_list')
    return render(request, 'stock/stock_confirm_delete.html', {'stock': stock})

# Expense CRUD Views
def expense_list(request):
    expenses = Expense.objects.order_by('-created_at')[:50]
    return render(request, 'expenses/expense_list.html', {'expenses': expenses})

def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense added successfully.')
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'expenses/expense_form.html', {'form': form})

def expense_update(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully.')
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/expense_form.html', {'form': form})

def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully.')
        return redirect('expense_list')
    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})

# Accounting Views
def accounting_view(request):
    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()
    
    # Calculate total bills excluding credits
    total_bills = Bill.objects.filter(created_at__date=selected_date, is_credit=False).aggregate(total=Coalesce(Sum('total'), Decimal('0.00')))['total']
    
    # Calculate total of credits paid today
    credits_paid_today_total = Bill.objects.filter(paid_at__date=selected_date, is_credit=True).aggregate(total=Coalesce(Sum('total'), Decimal('0.00')))['total']
    
    # Add credits paid to total bills
    total_bills += credits_paid_today_total
    
    # Calculate total expenses
    total_expenses = Expense.objects.filter(created_at__date=selected_date).aggregate(total=Coalesce(Sum('amount'), Decimal('0.00')))['total']
    
    # Calculate net accounting
    net_accounting = total_bills - total_expenses
    
    # Check if accounting for the selected date is already validated
    try:
        accounting = Accounting.objects.get(date=selected_date)
        is_validated = True
    except Accounting.DoesNotExist:
        accounting = None
        is_validated = False
    
    # Fetch bills for the selected date (excluding credits)
    bills_today = Bill.objects.filter(
        Q(created_at__date=selected_date, is_credit=False) |
        Q(paid_at__date=selected_date, is_credit=True)
    ).order_by('-created_at')[:50]
    
    # Fetch expenses for the selected date
    expenses_today = Expense.objects.filter(created_at__date=selected_date).order_by('-created_at')[:50]
    
    # Fetch credits paid today
    credits_paid_today = Bill.objects.filter(paid_at__date=selected_date, is_credit=True).order_by('-paid_at')
    
    context = {
        'selected_date': selected_date,
        'total_bills': total_bills,
        'total_expenses': total_expenses,
        'net_accounting': net_accounting,
        'is_validated': is_validated,
        'accounting': accounting,
        'bills_today': bills_today,
        'expenses_today': expenses_today,
        'credits_paid_today': credits_paid_today,
    }
    return render(request, 'accounting/accounting_view.html', context)

@csrf_protect
def validate_accounting(request):
    if request.method == 'POST':
        # Validate accounting for today
        today = timezone.now().date()
        
        # Calculate total bills excluding credits
        total_bills = Bill.objects.filter(created_at__date=today, is_credit=False).aggregate(total=Coalesce(Sum('total'), Decimal('0.00')))['total']
        
        # Calculate total of credits paid today
        credits_paid_today_total = Bill.objects.filter(paid_at__date=today, is_credit=True).aggregate(total=Coalesce(Sum('total'), Decimal('0.00')))['total']
        
        # Add credits paid to total bills
        total_bills += credits_paid_today_total
    
        # Calculate total expenses
        total_expenses = Expense.objects.filter(created_at__date=today).aggregate(total=Coalesce(Sum('amount'), Decimal('0.00')))['total']
        
        # Calculate net accounting
        net_accounting = total_bills - total_expenses
        
        # Check if accounting for today is already validated
        if Accounting.objects.filter(date=today).exists():
            messages.error(request, "Today's accounting has already been validated.")
            return redirect('accounting_view')
        
        # Create Accounting record
        Accounting.objects.create(
            date=today,
            total_sales=total_bills,
            total_expenses=total_expenses,
            net_accounting=net_accounting
        )
        messages.success(request, "Today's accounting has been validated successfully.")
        return redirect('accounting_view')
    else:
        messages.error(request, "Invalid request method.")
        return redirect('accounting_view')

def accounting_report(request):
    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()
    
    # Calculate total bills excluding credits
    total_bills = Bill.objects.filter(created_at__date=selected_date, is_credit=False).aggregate(total=Coalesce(Sum('total'), Decimal('0.00')))['total']
    
    # Calculate total of credits paid today
    credits_paid_today_total = Bill.objects.filter(paid_at__date=selected_date, is_credit=True).aggregate(total=Coalesce(Sum('total'), Decimal('0.00')))['total']
    
    # Add credits paid to total bills
    total_bills += credits_paid_today_total
    
    # Calculate total expenses
    total_expenses = Expense.objects.filter(created_at__date=selected_date).aggregate(total=Coalesce(Sum('amount'), Decimal('0.00')))['total']
    
    # Calculate net accounting
    net_accounting = total_bills - total_expenses
    
    # Check if accounting for the selected date is already validated
    try:
        accounting = Accounting.objects.get(date=selected_date)
        is_validated = True
    except Accounting.DoesNotExist:
        accounting = None
        is_validated = False
    
    # Fetch expenses for the selected date
    expenses_today = Expense.objects.filter(created_at__date=selected_date).order_by('-created_at')[:50]
    
    # Aggregate product sales for the selected date, excluding credits
    product_sales = BillItem.objects.filter(
        bill__created_at__date=selected_date,
        bill__is_credit=False
    ).values(
        'product__name',
        'product__price'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_sales=Sum('subtotal')
    ).order_by('product__name')
    
    # Fetch credits paid today
    credits_paid_today = Bill.objects.filter(paid_at__date=selected_date, is_credit=True).order_by('-paid_at')
    
    context = {
        'selected_date': selected_date,
        'total_bills': total_bills,
        'total_expenses': total_expenses,
        'net_accounting': net_accounting,
        'is_validated': is_validated,
        'accounting': accounting,
        'expenses_today': expenses_today,
        'product_sales': product_sales,
        'credits_paid_today': credits_paid_today,
    }
    return render(request, 'accounting/accounting_report.html', context)

def credit_list(request):
    credits = Bill.objects.filter(is_credit=True, paid_at__isnull=True).order_by('-created_at')
    return render(request, 'credits/credit_list.html', {'credits': credits})

@csrf_protect
def pay_credit(request, bill_id):
    if request.method == 'POST':
        bill = get_object_or_404(Bill, id=bill_id, is_credit=True, paid_at__isnull=True)
        bill.paid_at = timezone.now()
        bill.save()
        messages.success(request, f"Credit for {bill.client_name} has been marked as paid.")
        return redirect('credit_list')
    else:
        return HttpResponse(status=405)
