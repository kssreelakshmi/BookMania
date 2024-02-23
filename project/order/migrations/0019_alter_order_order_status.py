# Generated by Django 4.2.6 on 2024-02-16 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0018_alter_order_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('New', 'New'), ('Order placed', 'Order placed'), ('Accepted', 'Accepted'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'), ('Returned', 'Returned'), ('Payment Pending', 'Payment Pending')], default='New', max_length=20),
        ),
    ]