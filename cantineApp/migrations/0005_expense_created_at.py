# Generated by Django 5.1.1 on 2024-11-23 18:52

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cantineApp', '0004_remove_product_stock_stock'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
