# cantine/urls.py

from django.contrib import admin
from django.urls import path
from cantineApp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('caisse/', views.caisse, name='caisse'),
    path('bill/<int:bill_id>/', views.view_bill, name='view_bill'),
    path('bill/<int:bill_id>/details/', views.bill_details, name='bill_details'),
    path('add_to_bill/', views.add_to_bill, name='add_to_bill'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('stock/', views.stock_list, name='stock_list'),
    path('stock/add/', views.stock_create, name='stock_create'),
    path('stock/<int:pk>/edit/', views.stock_update, name='stock_update'),
    path('stock/<int:pk>/delete/', views.stock_delete, name='stock_delete'),
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/edit/', views.expense_update, name='expense_update'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    path('accounting/', views.accounting_view, name='accounting_view'),
    path('accounting/validate/', views.validate_accounting, name='validate_accounting'),
    path('accounting/report/', views.accounting_report, name='accounting_report'),
    
    # Added URL patterns for the credit functionality
    path('credits/', views.credit_list, name='credit_list'),
    path('credits/pay/<int:bill_id>/', views.pay_credit, name='pay_credit'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
