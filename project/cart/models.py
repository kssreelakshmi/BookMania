from django.db import models
from store.models import ProductVariant
from accounts.models import Account

# Create your models here.

class Cart(models.Model):
    cart_id =models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)
    
    
    def __str__(self):
        return self.cart_id
    
class Cart_item(models.Model):
    user = models.ForeignKey(Account, on_delete = models.CASCADE, null=True)
    product = models.ForeignKey(ProductVariant,on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
    quantity =  models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add = True)
    
    def sub_total(self):
        return self.product.sale_price * self.quantity
    
    
    def __str__(self):
        return self.product.get_product_name()
        
    