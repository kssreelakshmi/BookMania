from django.db import models
from accounts.models import Account
from accounts.models import Addresses
from store.models import ProductVariant

# Create your models here.

class PaymentMethod(models.Model):
    method_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.method_name

class Payment(models.Model):
    
    PAYMENT_STATUS_CHOICES =(
        ("PENDING", "Pending"),
        ("FAILED", "Failed"),
        ("SUCCESS", "Success"),
        )
    
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    method = models.ForeignKey(PaymentMethod,on_delete=models.CASCADE)
    payment_order_id = models.CharField(max_length=100,null=True,blank=True)
    payment_signature = models.CharField(max_length=100,null=True,blank=True)
    payment_status = models.CharField(choices = PAYMENT_STATUS_CHOICES, null=True, max_length=20)
    payment_id = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add = True)
    
    def __str__(self):
        return self.payment_id


class Order(models.Model):
    
    ORDER_STATUS_CHOICES = (
        
        ("New", "New"),
        ("Order placed", "Order placed"),
        ("Accepted", "Accepted"),
        ("Delivered", "Delivered"),
        ("Cancelled by Admin", "Cancelled by Admin"),
        ("Cancelled by User", "Cancelled by User"),
        ("Returned", "Returned"),
        )
    
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    order_id = models.CharField(max_length=100)
    address = models.ForeignKey(Addresses,on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment,on_delete=models.SET_NULL, null=True, blank=True)
    order_instruction = models.CharField(max_length=100, blank=True, null=True)
    order_total = models.DecimalField(max_digits=50, decimal_places=2)
    is_ordered = models.BooleanField(default=False)
    tax = models.DecimalField(max_digits=50, decimal_places=2, null=True)
    order_status = models.CharField(choices = ORDER_STATUS_CHOICES, max_length=20, default='New')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip = models.CharField(max_length=50, blank=True)
    # cancellation_requested = models.BooleanField(default=False)
    # return_requested = models.BooleanField(default=False)
    
    
    def __str__(self):
        return self.order_id
    

class OrderProduct(models.Model):
    
    user = models.ForeignKey(Account, on_delete=models.SET_NULL,null=True)
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant,on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null = True)
    quantity = models.IntegerField()
    product_price = models.DecimalField(max_digits=12, decimal_places=2)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def price_in_order_product(self):
        return self.product_price*self.quantity    
    
    def __str__(self):
        return str(self.order)
    
class OrderCancel(models.Model):
    user = models.ForeignKey(Account,on_delete = models.CASCADE)
    order = models.ForeignKey(Order,on_delete=models.CASCADE)

class OrderReturn(models.Model):
    pass
