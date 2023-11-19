from django.shortcuts import render,redirect
from django.urls import reverse
from cart.models import Cart_item
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from.models import Order,PaymentMethod
import datetime
from accounts.forms import Addresses
import razorpay
from django.conf import settings

# Create your views here.

def order_summary(request):
    current_user =request.user
    cart_items = Cart_item.objects.filter(user = current_user)
    cart_count = cart_items.count()
    
    if cart_count <= 0:
        return redirect("shop")
    order_total = 0
    tax = 0
    grand_total = 0    
    
    for cart_item in cart_items:
         order_total += cart_item.sub_total()
    tax = (5 * order_total) / 100
    grand_total = order_total + tax
    
    if request.method == 'POST':
        address_id = int(request.POST.get('address1'))
        if address_id is None:
            messages.error(request, "Please choose an address")
            return redirect('cart_checkout')
        data = Order()
        
        try:
            shipping_address = Addresses.objects.get(id=address_id)
            print(shipping_address.name)
        except:
            messages.error(request, "Please choose an address")
            return redirect('cart_checkout')
        
        data.user = current_user
        data.tax = tax
        data.order_total = grand_total
        data.address = shipping_address
        data.order_instruction = request.POST.get("delivery_note")
        data.ip = request.META.get('REMOTE_ADDR')
        data.save()
    
        current_datetime = datetime.datetime.now()
        current_year = current_datetime.strftime("%Y")
        current_month = current_datetime.strftime("%m")
        current_day = current_datetime.strftime("%d")
        current_hour = current_datetime.strftime("%H")
        current_minute = current_datetime.strftime("%M")
        concatenated_datetime = current_year + current_month + current_day + current_hour + current_minute
        
        order_number = 'BM-ORD'+concatenated_datetime+str(data.pk)
        data.order_id = order_number
        data.save()
        
        order = Order.objects.get(user=current_user,is_ordered=False,order_id=order_number)
        payment_method = PaymentMethod.objects.filter(is_active=True)
        
        context = { 
            'order': order,
            'cart_items': cart_items,
            'grand_total': grand_total,
            'total': order_total,
            'tax': tax,
            'shipping_address': shipping_address,
            'payment_methods': payment_method,
            }
        
        return render(request,'store_templates/order_summary.html',context)
    else:
        
        messages.error(request, 'Please choose a payment option ')
        return redirect('cart_checkout')
       
def place_order(request):
    current_user = request.user
    order = Order.objects.filter(user=current_user,is_completed=False).exists()
    if not order:
        return redirect('order_summary')
    cart_items = Cart_item.objects.get(user=current_user)
    cart_item_count =cart_items.count()
    
    if cart_item_count <= 0:
        return redirect('shop')
    
    order_total = 0
    tax=0
    
    for cart_item in cart_items:
        order_total += cart_item.sub_total()
    tax =(5 * order_total)/100
    
    if request.method == "POST":
        
        order_id = request.POST.get('order_id_summary')
        payment_method = request.POST.get('payment1')
        
        if not payment_method:
            messages.error(request,'Please Choose a Payment Method !!')
            return redirect('order_summary')
        
        try:
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_id)
            
        except Exception as e:
            print(e)
            
        try:  
            if order.order_total == 0:
                raise Exception
            if payment_method == 'RAZORPAY':
                client = razorpay.Client(auth=(settings.razor_pay_key_id,settings.key_secret))
                payment = client.order.create({'amount':float(order.order_total) * 100,"currency": "INR"})  
            else:
                payment = False 
        except :
            payment = False
        
        success_url = request.build_absolute_uri(reverse('payment-success'))
        failed_url = request.build_absolute_uri(reverse('payment-failed'))

                
                                
        
        
    
    
    return render(request,'store_templates/place_order.html')


