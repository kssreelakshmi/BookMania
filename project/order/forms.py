from django import forms
from .models import Order,OrderProduct
    
    
class OrderStatusForm(forms.ModelForm):

      class Meta:
            model = Order
            fields = ['order_status']

class OrderProductStatusForm(forms.ModelForm):

      class Meta:
            model = OrderProduct
            fields = ['order_status']
