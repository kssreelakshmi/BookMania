# Generated by Django 4.2.6 on 2023-11-17 04:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_alter_order_order_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='order_number',
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('New', 'New'), ('Order placed', 'Order placed'), ('Accepted', 'Accepted'), ('Delivered', 'Delivered'), ('Cancelled by Admin', 'Cancelled by Admin'), ('Cancelled by User', 'Cancelled by User'), ('Returned', 'Returned')], default='New', max_length=20),
        ),
    ]
