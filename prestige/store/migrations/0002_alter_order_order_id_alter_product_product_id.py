# Generated by Django 5.1.6 on 2025-03-19 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="order_id",
            field=models.PositiveIntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="product_id",
            field=models.PositiveIntegerField(unique=True),
        ),
    ]
