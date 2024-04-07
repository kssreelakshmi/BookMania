from django.shortcuts import render,redirect
from django.urls import reverse
from cart.models import Cart_item
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from .models import Order,PaymentMethod,Payment,OrderProduct,Invoice
from store.models import Product,ProductVariant
from coupon.models import Coupon
import datetime
from accounts.models import Addresses, ShippingAddress
import razorpay
import json
from django.views.decorators.cache import cache_control
from django.http import JsonResponse
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from io import BytesIO
from django.template.loader import get_template,render_to_string
from xhtml2pdf import pisa
from django.db.models import Sum
import calendar
import pytz
from django.utils import timezone



# Create your views here.
@login_required(login_url='signin')
def order_summary(request):
    current_user =request.user
    cart_items = Cart_item.objects.filter(user = current_user)
    cart_count = cart_items.count()
    
    if cart_count <= 0:
        return redirect("shop")
    order_total = 0
    
    for cart_item in cart_items:
         order_total += cart_item.sub_total()
    
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        try:
            data = Order.objects.get(order_id = order_id, is_ordered = False)
        except Exception as e:
            data = Order()
            print(e)

        address_id = int(request.POST.get('address1'))
        if address_id is None:
            messages.error(request, "Please choose an address")
            return redirect('cart_checkout')
        
        Order.objects.filter(user = current_user, payment = None).exclude(order_id = data.order_id).delete()
        
        try:
            shipping_address = Addresses.objects.get(id=address_id)
        except:
            messages.error(request, "Please choose an address")
            return redirect('cart_checkout')
        
        order_address = ShippingAddress()
        order_address.name = shipping_address.name
        order_address.phone_number = shipping_address.phone_number
        order_address.address_line_1 = shipping_address.address_line_1
        order_address.address_line_2 = shipping_address.address_line_2
        order_address.city = shipping_address.city
        order_address.state = shipping_address.state
        order_address.country = shipping_address.country.name
        order_address.pincode = shipping_address.pincode
        order_address.save()

        data.shipping_address = order_address
        data.order_instruction = request.POST.get("delivery_note")
        data.save()
        
        payment_method = PaymentMethod.objects.filter(is_active=True)
        coupons = Coupon.objects.filter(is_active=True, expire_date__gt=datetime.date.today())
        context = { 
            'coupons' : coupons,
            'order': data,
            'cart_items': cart_items,
            'grand_total': data.order_total,
            'total': order_total,
            'tax': data.tax,
            'coupon_discount': data.coupon_discount,
            'shipping_address': data.shipping_address,
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
    if request.method == "POST":  
        order_id = request.POST.get('order_id_summary')
        payment_id= request.POST.get('payment1')
        if not payment_id:
            messages.error(request,'Please Choose a Payment Method !!')
            return redirect('order_summary')
        
        payment_method = PaymentMethod.objects.get(id = payment_id)
        
        try:
            order = Order.objects.get(user=current_user, is_ordered=False, order_id=order_id)
            
        except Exception as e:
            print(e)
            
        try:  
            if order.order_total == 0:
                raise Exception
            if payment_method.method_name == 'RAZORPAY':
                client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID,settings.KEY_SECRET))
                payment = client.order.create({'amount':float(order.order_total) * 100,"currency": "INR"}) 
                
            else:
                payment = False 
        except:
            payment = False
        
        success_url = request.build_absolute_uri(reverse('payment_success'))
        failed_url = request.build_absolute_uri(reverse('payment_failed'))
        context = {
            'order': order,
            'cart_items': cart_items,
            'grand_total': order.order_total,
            'razor_pay_key_id': settings.RAZOR_PAY_KEY_ID,
            'razor_pay_secret_key': settings.KEY_SECRET,
            'total': order_total,
            'payment': payment,
            'tax': order.tax,
            'coupon_discount' : order.coupon_discount,
            'shipping_address': order.shipping_address,
            'payment_method': payment_method,
            'success_url': success_url,
            'failed_url': failed_url,
            }
        return render(request,'store_templates/place_order.html',context)
    else:
        return redirect('order_summary')
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
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
            order.order_status = 'New'
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

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def payment_failed(request):
    payment_method = request.GET['method']
    order_id = request.GET['order_id']
    try:
        order = Order.objects.get(user=request.user,is_ordered=False,order_id=order_id)
        payment_method = PaymentMethod.objects.get(method_name = payment_method)
    except Exception as e:
        print(e)

    payment_id = request.GET['error_payment_id']                
    payment_order_id = request.GET['error_order_id']
    payment_amount = request.GET['payment_amount']
    error_reason = request.GET['error_reason']
    error_description = request.GET['error_description']
    payment = Payment(
        user = request.user,
        payment_id = payment_id,
        payment_order_id = payment_order_id,
        method = payment_method,
        amount_paid = payment_amount,
        error_reason = error_reason,
        error_description = error_description,
        payment_status = 'FAILED',
        )
    payment.save()
    order.payment = payment
    order.is_ordered = False
    order.order_status = 'Payment Pending'
    order.save()

    cart_items = Cart_item.objects.filter(user=request.user)
            
    for cart_item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order.id
        order_product.user_id = request.user.id
        order_product.quantity = cart_item.quantity
        order_product.variant_id = cart_item.product.id
        order_product.product_price = cart_item.product.sale_price
        order_product.is_ordered = False
        order_product.save()
    context = {
        'payment_method' : payment_method,
        # 'error_code' : request.GET['error_code'],
        'error_description' :  error_description,
        'error_reason' : error_reason,
        'error_payment_id' : payment_id,
        'error_order_id' : payment_order_id,
    }

    return render(request,'store_templates/order_failed.html',context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def retry_payment(request):

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.method=='POST' and is_ajax:

        order_id = request.POST.get('order_id')

        try:
            order = Order.objects.get(user = request.user, is_ordered = False, order_id = order_id)
        except Exception as e:
            print(e)

        client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID,settings.KEY_SECRET))
        payment = client.order.create({'amount':float(order.order_total) * 100,"currency": "INR"}) 
        success_url = request.build_absolute_uri(reverse('payment_success'))
        failed_url = request.build_absolute_uri(reverse('payment_failed'))
                
        if payment:
            return JsonResponse(
                {
                    'status' : 'SUCCESS',
                    'name' : order.user.username,
                    'email' : order.user.email,
                    'contact' : order.user.phone_number,
                    'payment_id': payment['id'],
                    'payment_amount': payment['amount'],

                    'razor_pay_key_id': settings.RAZOR_PAY_KEY_ID,
                    'razor_pay_secret_key': settings.KEY_SECRET,
                    'success_url': success_url,
                    'failed_url': failed_url,
                    }
                    )
        else:
            return JsonResponse(
                {
                    'status' : 'FAILED',
                    'reason': 'Oops its not you, its us ! Please try again',
                    }
                    )
        
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_completed(request):
    try:
        if (request.session['order_id'] and request.session['payment_id']):
            order_id = request.session['order_id']
            payment_id   = request.session['payment_id']
            
            try:
                order = Order.objects.get(order_id = order_id, is_ordered = True)
                ordered_products = OrderProduct.objects.filter(order_id = order.id)
                total = 0
                tax = 0 
                
                for item in ordered_products:
                    total += item.product_price * item.quantity
                payment = Payment.objects.get(payment_id=payment_id)

                invoice = Invoice()
                invoice.order = order
                invoice.save()

                context = {

                    'order' : order,
                    'order_id' :order_id,
                    'total' :total,
                    'tax' : order.tax,
                    'coupon_discount' : order.coupon_discount,
                    'grand_total' : order.order_total,
                    'payable_amount' : order.order_total,
                    'ordered_products' : ordered_products,
                    'payment' :payment,
                    'invoice' : invoice,
                    
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
    
def generate_invoice(request,invoice_number):
    try:
        invoice = Invoice.objects.get(invoice_number = invoice_number)
    except:
        messages.warning(request, 'Invoice not generated for this order !')
    
    try:
        order_products = OrderProduct.objects.filter(order = invoice.order,is_ordered = True)

    except Exception as e:
        print(e)
    sub_total = 0
    for item in order_products:
        sub_total += item.product_price * item.quantity

    template_path = 'base/user_side/invoice.html'
    context = {
        'invoice': invoice,
        'ordered_products': order_products,
        'sub_total': sub_total,
        'payable_amount': invoice.order.order_total,
        'order': invoice.order,
        'coupon_discount' : invoice.order.coupon_discount,

        }
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="{invoice.invoice_number}.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


