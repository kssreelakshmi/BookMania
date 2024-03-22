# Generated by Django 4.2.6 on 2024-03-21 11:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('coupon', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(max_length=100)),
                ('coupon_discount', models.DecimalField(blank=True, decimal_places=2, max_digits=50, null=True)),
                ('order_instruction', models.CharField(blank=True, max_length=100, null=True)),
                ('order_total', models.DecimalField(decimal_places=2, max_digits=50)),
                ('is_ordered', models.BooleanField(default=False)),
                ('tax', models.DecimalField(decimal_places=2, max_digits=50, null=True)),
                ('order_status', models.CharField(choices=[('New', 'New'), ('Order placed', 'Order placed'), ('Accepted', 'Accepted'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'), ('Returned', 'Returned'), ('Payment Pending', 'Payment Pending'), ('Partially Cancelled', 'Partially Cancelled'), ('Partially Returned', 'Partially Returned'), ('Completed', 'Completed'), ('Cancel or Return Requested', 'Cancel or Return Requested')], default='New', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ip', models.CharField(blank=True, max_length=50)),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.addresses')),
                ('coupon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coupon.coupon')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method_name', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_order_id', models.CharField(blank=True, max_length=100, null=True)),
                ('payment_signature', models.CharField(blank=True, max_length=100, null=True)),
                ('payment_status', models.CharField(choices=[('PENDING', 'Pending'), ('FAILED', 'Failed'), ('SUCCESS', 'Success')], max_length=20, null=True)),
                ('error_description', models.TextField(blank=True, max_length=500, null=True)),
                ('error_reason', models.CharField(blank=True, max_length=500, null=True)),
                ('payment_id', models.CharField(max_length=100)),
                ('amount_paid', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('method', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.paymentmethod')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('product_price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('is_ordered', models.BooleanField(default=False)),
                ('order_status', models.CharField(choices=[('New', 'New'), ('Order placed', 'Order placed'), ('Accepted', 'Accepted'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'), ('Returned', 'Returned'), ('Cancellation Requested', 'Cancellation Requested'), ('Cancellation Rejected', 'Cancellation Rejected'), ('Return Requested', 'Return Requested'), ('Return Rejected', 'Return Rejected')], default='New', max_length=100)),
                ('cancellation_reason', models.CharField(choices=[(' I have bought the wrong item', ' I have bought the wrong item'), ('I have found a cheaper alternative for lesser price.', 'I have found a cheaper alternative for lesser price.'), ('I have provided the wrong address.', 'I have provided the wrong address.'), ('Expected delivery date has changed and the product is arriving at a later date.', 'Expected delivery date has changed and the product is arriving at a later date.'), ('Product is not required anymore.', 'Product is not required anymore.'), ('Bad review from friends/relatives after ordering the product.', 'Bad review from friends/relatives after ordering the product.'), ('Product is taking too long to be delivered', ' Product is taking too long to be delivered'), ('other', 'other')], default='Not cancelled', max_length=500)),
                ('return_reason', models.CharField(choices=[('Wrong product ordered', 'Wrong product ordered'), ('Product is not required anymore.', 'Product is not required anymore.'), ('The product was damaged or defective.', 'The product was damaged or defective.'), ('The quality of product was cheap', 'The quality of product was cheap'), ('The product arrived late ', 'The product arrived late'), ('Wrong product shipped', 'Wrong product shipped'), ('Wardrobing', 'Wardrobing'), ('other', 'other')], default='Not returned', max_length=500)),
                ('others', models.TextField(blank=True, max_length=500, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.order')),
                ('payment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='order.payment')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.productvariant')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='order.payment'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(max_length=30)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.order')),
            ],
        ),
    ]
