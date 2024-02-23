# Generated by Django 4.2.6 on 2024-02-14 06:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0008_order_cancellation_requested_order_return_requested_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cancellationreasons',
            name='orderProduct',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='order.orderproduct'),
        ),
        migrations.AddField(
            model_name='returnreasons',
            name='orderProduct',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='order.orderproduct'),
        ),
    ]