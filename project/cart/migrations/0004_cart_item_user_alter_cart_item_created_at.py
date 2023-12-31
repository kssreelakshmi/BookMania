# Generated by Django 4.2.6 on 2023-11-07 14:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cart', '0003_cart_item_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart_item',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='cart_item',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
