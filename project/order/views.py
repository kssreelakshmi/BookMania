from django.shortcuts import render,redirect
from django.urls import reverse
from cart.models import Cart_item
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from .models import Order,PaymentMethod,Payment,OrderProduct
from store.models import Product,ProductVariant
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
    order_exist = Order.objects.filter(user=current_user,is_ordered=False).exists()
    if not order_exist:
        return redirect('order_summary')
    cart_items = Cart_item.objects.filter(user=current_user)
    cart_item_count =cart_items.count()
    
    if cart_item_count <= 0:
        return redirect('shop')
    
    order_total = 0
    tax=0
    
    for cart_item in cart_items:
        order_total += cart_item.sub_total()
    tax =(5 * order_total)/100
    grand_total = order_total + tax
    if request.method == "POST":  
        order_id = request.POST.get('order_id_summary')
        payment_id= request.POST.get('payment1')
        if not payment_id:
            messages.error(request,'Please Choose a Payment Method !!')
            return redirect('order_summary')
        
        payment_method = PaymentMethod.objects.get(id = payment_id)
        print(payment_method)
        
        try:
            order = Order.objects.get(user=current_user, is_ordered=False, order_id=order_id)
            print(order)
            
        except Exception as e:
            print(e)
            
        try:  
            if order.order_total == 0:
                raise Exception
            if payment_method.method_name == 'RAZORPAY':
                client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID,settings.KEY_SECRET))
                payment = client.order.create({'amount':float(order.order_total) * 100,"currency": "INR"}) 
                print('sreeeeeee33333333333')
                for key, value in payment.items():
                    print(key,'  :  ',value)
            else:
                print("sreeeeeeeeeeeeeeeeee")
                payment = False 
        except :
            print("aaradh")
            payment = False
        
        success_url = request.build_absolute_uri(reverse('payment_success'))
        failed_url = request.build_absolute_uri(reverse('payment_failed'))
        context = {
            'order': order,
            'cart_items': cart_items,
            'grand_total': grand_total,
            'razor_pay_key_id': settings.RAZOR_PAY_KEY_ID,
            'razor_pay_secret_key': settings.KEY_SECRET,
            'total': order_total,
            'payment': payment,
            'tax': tax,
            'shipping_address': order.address,
            'payment_method': payment_method,
            'success_url': success_url,
            'failed_url': failed_url,
            }
        return render(request,'store_templates/place_order.html',context)
    else:
        return redirect('order_summary')

def payment_success(request):
   
    payment_method = request.GET['method']
    order_id = request.GET['order_id']
    try:
        order = Order.objects.get(user=request.user,is_ordered=False,order_id=order_id)
    
    except Exception as e:
        print(e)
        return redirect('user_home')   
    
    payment_method_is_active = PaymentMethod.objects.filter(method_name=payment_method,is_active=True).exists()
    
    if payment_method == 'COD':
        if payment_method_is_active:
            payment_method = PaymentMethod.objects.get(method_name=payment_method,is_active=True)  
            
            payment = Payment(
                user = request.user,
                payment_id = 'COD-'+order_id,
                payment_order_id = order_id,
                payment_signature = 'Signed',   
                method = payment_method,
                amount_paid = order.order_total,
                payment_status = 'SUCCESS',
                )
            payment.save()
            
            order.payment = payment
            order.is_ordered = True
            order.save()
            
            cart_items = Cart_item.objects.filter(user=request.user)
            
            for cart_item in cart_items:
                order_product = OrderProduct()
                order_product.order_id = order.id
                order_product.user_id = request.user.id
                order_product.quantity = cart_item.quantity
                order_product.variant_id = cart_item.product.id
                order_product.product_price = cart_item.product.sale_price
                order_product.is_ordered = True
                order_product.save()
            
                product_variant = ProductVariant.objects.get(id=cart_item.product.id)
                product_variant.stock -= cart_item.quantity
                product_variant.save()
            
            Cart_item.objects.filter(user=request.user).delete()
            
            request.session["order_id"] = order.order_id
            request.session["payment_id"] = payment.payment_id
            return redirect('order_completed')
        else:
            messages.error(request, "COD is not currently available")
            return redirect('cart_checkout')   
            
    elif payment_method == 'RAZORPAY':
        
        payment_id = request.GET['payment_id']                
        payment_order_id = request.GET['payment_order_id']
        payment_sign = request.GET['payment_sign']
        payment_amount = request.GET['payment_amount']
        
        payment_method = PaymentMethod.objects.get(method_name = payment_method)

        if payment_method_is_active:
            payment = Payment(
                user = request.user,
                payment_id = payment_id,
                payment_order_id = payment_order_id,
                payment_signature = payment_sign,   
                method = payment_method,
                amount_paid = payment_amount,
                payment_status = 'SUCCESS',
                )
            payment.save()
            
            order.payment = payment
            order.is_ordered = True
            order.save()

            cart_items = Cart_item.objects.filter(user=request.user)
            
            for cart_item in cart_items:
                order_product = OrderProduct()
                order_product.order = order
                order_product.user_id = request.user.id
                order_product.quantity = cart_item.quantity
                order_product.variant_id = cart_item.product.id
                order_product.product_price = cart_item.product.sale_price
                order_product.is_ordered = True
                order_product.save()
            
                product_variant = ProductVariant.objects.get(id=cart_item.product.id)
                product_variant.stock -= cart_item.quantity
                product_variant.save()
            
            
            Cart_item.objects.filter(user=request.user).delete()
            
            request.session["order_id"] = order.order_id
            request.session["payment_id"] = payment_id
            return redirect('order_completed')
        else:
            messages.error(request, "Invalid Payment Method Found")
            return redirect('payment_failed')
    
    else:
        return redirect('user_dashboard')    
                        
def payment_failed(request):
    context = {
        'payment_method' : request.GET['method'],
        'error_code' : request.GET['error_code'],
        'error_description' :  request.GET['error_description'],
        'error_reason' : request.GET['error_reason'],
        'error_payment_id' : request.GET['error_payment_id'],
        'error_order_id' : request.GET['error_order_id'],
    }

    return render(request,'store_templates/order_failed.html',context)


def order_completed(request):
    print('from complete reached')
    try:
        print('from complete page22222')
        if (request.session['order_id'] and request.session['payment_id']):
            order_id = request.session['order_id']
            print(order_id) 
            payment_id   = request.session['payment_id']
            
            try:
                order = Order.objects.get(order_id = order_id, is_ordered = True)
                ordered_products = OrderProduct.objects.filter(order_id = order.id)
                total = 0
                tax = 0 
                
                for item in ordered_products:
                    total += item.product_price * item.quantity
                tax = (5*total)/100
                grand_total = total + tax
                payment = Payment.objects.get(payment_id=payment_id)
                
                context = {
                    'order' : order,
                    'order_id' :order_id,
                    'total' :total,
                    'tax' : tax,
                    'grand_total' : grand_total,
                    'payable_amount' : order.order_total,
                    'ordered_products' : ordered_products,
                    'payment' :payment
                    
                }   
                
                # del request.session['order_id']
                # del request.session['payment_id']
                return render(request,'store_templates/order_completed.html',context)
            
            except Exception as e:
                print(e)
                return redirect('user_home')
    except Exception as e:
        print(e)
        return redirect('user_home')
        