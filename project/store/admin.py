from django.contrib import admin
from django.db import models
from .models import Product, ProductVariant, Attribute, AttributeValue, Author, Publication,AdditionalProductImages,ReviewRating,RecentViewedProduct

# Register your models here.


admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(Attribute)
admin.site.register(AttributeValue)
admin.site.register(Publication)
admin.site.register(Author)
admin.site.register(AdditionalProductImages)
admin.site.register(ReviewRating)
admin.site.register(RecentViewedProduct)
