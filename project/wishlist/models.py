from django.db import models
from accounts.models import Account
from store.models import ProductVariant

# Create your models here.

class Wishlist(models.Model):
    wishlist_name = models.CharField(max_length=200, default='my wishlist')
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_default = models.BooleanField(default=False) 

    def __str__(self):
        return self.user.username + ' ' + self.wishlist_name



class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete = models.CASCADE)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, blank=True, null = True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_variant.get_product_name()