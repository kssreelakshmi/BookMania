# Generated by Django 4.2.6 on 2024-02-23 07:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0001_initial'),
        ('order', '0027_alter_order_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='coupon',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coupon.coupon'),
        ),
        migrations.AddField(
            model_name='order',
            name='coupon_discount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=50, null=True),
        ),
    ]
