# Generated by Django 4.2.6 on 2023-10-30 05:08

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0002_alter_cart_item_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart_item',
            name='created_at',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
