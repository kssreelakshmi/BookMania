from django.db import models
from accounts.models import Account,ShippingAddress
from accounts.models import Addresses
from store.models import ProductVariant
from coupon.models import Coupon

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
    error_description = models.TextField(max_length=500,null=True,blank=True)
    error_reason = models.CharField(max_length=500,null=True,blank=True)
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
        ("Cancelled", "Cancelled"),
        ("Returned", "Returned"),
        ("Payment Pending", "Payment Pending"),
        ("Partially Cancelled", "Partially Cancelled"),
        ("Partially Returned", "Partially Returned"),
        ("Completed", "Completed"),
        # user choices
        ('Cancel or Return Requested', 'Cancel or Return Requested'),
        )

    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(ShippingAddress,on_delete=models.CASCADE, null=True, blank=True)
    order_id = models.CharField(max_length=100)
    coupon = models.ForeignKey(Coupon, on_delete = models.DO_NOTHING, null=True, blank = True)
    coupon_discount = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    payment = models.ForeignKey(Payment,on_delete=models.SET_NULL, null=True, blank=True)
    order_instruction = models.CharField(max_length=100, blank=True, null=True)
    order_total = models.DecimalField(max_digits=50, decimal_places=2)
    is_ordered = models.BooleanField(default=False)
    tax = models.DecimalField(max_digits=50, decimal_places=2, null=True)
    order_status = models.CharField(choices = ORDER_STATUS_CHOICES, max_length=100, default='New')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip = models.CharField(max_length=50, blank=True)
    
    
    def __str__(self):
        return self.order_id
    

class OrderProduct(models.Model):
    STATUS_CHOICES = (
        
        ("New", "New"),
        ("Order placed", "Order placed"),
        ("Accepted", "Accepted"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
        ("Returned", "Returned"),
        ('Cancellation Requested', 'Cancellation Requested'),
        ('Cancellation Rejected', 'Cancellation Rejected'),
        ('Return Requested', 'Return Requested'),
        ('Return Rejected', 'Return Rejected')
        )
    
    ORDER_CANCEL_CHOICES = (
        
        (" I have bought the wrong item", " I have bought the wrong item"),
        ("I have found a cheaper alternative for lesser price.", "I have found a cheaper alternative for lesser price."),
        ("I have provided the wrong address.", "I have provided the wrong address."),
        ("Expected delivery date has changed and the product is arriving at a later date.", "Expected delivery date has changed and the product is arriving at a later date."),
        ("Product is not required anymore.", "Product is not required anymore."),
        ("Bad review from friends/relatives after ordering the product.", "Bad review from friends/relatives after ordering the product."),
        ("Product is taking too long to be delivered", " Product is taking too long to be delivered"),
        ("other","other")
        )

    ORDER_RETURN_CHOICES = (
        
        ("Wrong product ordered","Wrong product ordered"),
        ("Product is not required anymore.", "Product is not required anymore."),
        ("The product was damaged or defective.", "The product was damaged or defective."),
        ("The quality of product was cheap", "The quality of product was cheap"),
        ("The product arrived late ", "The product arrived late"),
        ("Wrong product shipped", "Wrong product shipped"),
        ("Wardrobing", "Wardrobing"),
        ("other","other"),
        )
    
    
    user = models.ForeignKey(Account, on_delete=models.SET_NULL,null=True)
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant,on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null = True)
    quantity = models.IntegerField()
    product_price = models.DecimalField(max_digits=12, decimal_places=2)
    is_ordered = models.BooleanField(default=False)

    order_status = models.CharField(choices = STATUS_CHOICES, max_length=100, default='New')
    cancellation_reason = models.CharField(choices = ORDER_CANCEL_CHOICES, max_length=500, default='Not cancelled')
    return_reason = models.CharField(choices = ORDER_RETURN_CHOICES, max_length=500, default='Not returned')
    others = models.TextField(max_length = 500, null = True, blank = True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def price_in_order_product(self):
        return self.product_price*self.quantity
    
    def __str__(self):
        return str(self.order)
    

class Invoice(models.Model):
    invoice_number = models.CharField(max_length=30)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.invoice_number

    def save(self, *args, **kwargs):
        self.invoice_number = 'BMIV-0' + str(Invoice.objects.all().count() + 1)
        super(Invoice, self).save(*args, **kwargs)


