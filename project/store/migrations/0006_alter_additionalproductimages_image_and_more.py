# Generated by Django 4.2.6 on 2024-03-20 05:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import store.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0005_alter_productvariant_stock'),
    ]

    operations = [
        migrations.AlterField(
            model_name='additionalproductimages',
            name='image',
            field=models.ImageField(upload_to='photos/product-variant/additional-images', validators=[store.models.validate_file_type]),
        ),
        migrations.AlterField(
            model_name='productvariant',
            name='thumbnail_image',
            field=models.ImageField(upload_to='photos/product-variant/thumbnail', validators=[store.models.validate_file_type]),
        ),
        migrations.CreateModel(
            name='ReviewRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(blank=True, max_length=200)),
                ('review', models.TextField(blank=True, max_length=500)),
                ('rating', models.FloatField()),
                ('ip', models.CharField(blank=True, max_length=50)),
                ('status', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product_variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.productvariant')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
