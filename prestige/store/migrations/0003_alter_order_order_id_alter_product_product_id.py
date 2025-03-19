# Generated by Django 5.1.6 on 2025-03-19 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0002_alter_order_order_id_alter_product_product_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="order_id",
            field=models.PositiveIntegerField(editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="product_id",
            field=models.PositiveIntegerField(editable=False, unique=True),
        ),
    ]
