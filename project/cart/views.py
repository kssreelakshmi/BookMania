from django.shortcuts import render,redirect
from store.models import ProductVariant
from accounts.models import Addresses
from accounts.forms import AddressForm
from cart.models import Cart,Cart_item
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from order.models import Order
import json
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart =  request.session.create()
    return cart


def Add_to_cart(request,product_id=None):
    
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if product_id:
        product = ProductVariant.objects.get(id=product_id)
    
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()
    if request.method =='POST' and is_ajax:
        data = json.load(request)
        product_id = int(data['productVariantId'])
        cart_action = data['selected_option']
        product = ProductVariant.objects.get(id=product_id)
        if request.user.is_authenticated:
            cart_item = Cart_item.objects.get(product=product,user=request.user)
            cart_items = Cart_item.objects.filter(user=request.user, is_active=True).order_by('-created_at')
        else:
            cart_item = Cart_item.objects.get(product=product,cart=cart)
            cart_items = Cart_item.objects.filter(cart=cart, is_active=True).order_by('-created_at')
            
        if cart_action == '+':
            if cart_item.product.stock == cart_item.quantity:
                return JsonResponse({
                    'status': 'Stock_limit_reached'
                })
        
            try:
                cart_item.quantity += 1 
            except Cart_item.DoesNotExist:
                pass
            
            cart_item.save()
            
            total = 0
            for cart_itm in cart_items:
                total += (cart_itm.product.sale_price * cart_itm.quantity)
            tax = (5*total)/100
            grand_total = total + tax
            
            return JsonResponse({
            'status': 'success',
            'cart_item_total': cart_item.sub_total(),
            'cart_item_qty': cart_item.quantity,
            'total': total,
            'tax': tax,
            'grand_total': grand_total
            })
        else:
            if cart_action == '-':
                if cart_item.quantity>1:
                    cart_item.quantity -= 1
                    cart_item.save()
                    
                    total = 0
                    for cart_itm in cart_items:
                        total += (cart_itm.product.sale_price * cart_itm.quantity)
                    tax = (5*total)/100
                    grand_total = total + tax
                
                else:
                    cart_item.delete()
                    return JsonResponse({
                        'status': 'cart_item_empty',
                        'message' : 'cart item will be deleted'
                    })
                    
                return JsonResponse({
                'status': 'success',
                'cart_item_total': cart_item.sub_total(),
                'cart_item_qty': cart_item.quantity,
                'total': total,
                'tax': tax,
                'grand_total': grand_total
                })
    else:
        if request.user.is_authenticated:
            try:
                cart_item = Cart_item.objects.get(product=product,user=request.user)
                cart_item.quantity += 1 
                cart_item.save()
            except Cart_item.DoesNotExist:
                    cart_item = Cart_item.objects.create(
                        user = request.user,
                        product = product,
                        quantity = 1,
                        cart = cart
                    )
        else:
            try:
                cart_item = Cart_item.objects.get(product=product,cart=cart)
                cart_item.quantity += 1 
                cart_item.save()
            except Cart_item.DoesNotExist:
                    cart_item = Cart_item.objects.create(
                        product = product,
                        quantity = 1,
                        cart = cart
                    )
            
        cart_item.save()
        return redirect(request.META['HTTP_REFERER'])

def Remove_cart_item(request,product_id):
    
    product = get_object_or_404(ProductVariant, id=product_id)
    if request.user.is_authenticated:
        cart_item = Cart_item.objects.get(product=product, user=request.user)
    else:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_item = Cart_item.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')


def cart(request,total=0,quantity=0,cart_items=None):
    
    try:
        tax = 0
        grand_total = 0
        total = 0
        if request.user.is_authenticated:
            cart_items = Cart_item.objects.filter(user=request.user, is_active=True).order_by('-created_at')
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = Cart_item.objects.filter(cart=cart, is_active=True).order_by('-created_at')
            
        for cart_item in cart_items:
            total += (cart_item.product.sale_price * cart_item.quantity)
        tax = (5*total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    context = {
        'total' : total,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total' : grand_total
    }
    return render(request,'store_templates/cart.html',context)


@login_required (login_url="user_login")
def Cart_checkout(request,total=0,cart_items=None,quantity=0):
    try:
        tax=0
        grand_total= 0
        cart_items = Cart_item.objects.filter(user=request.user,is_active=True)
        if not cart_items:
            return redirect('shop')
        for cart_item in cart_items:
            total += cart_item.product.sale_price * cart_item.quantity 
            quantity += cart_item.quantity
        tax = (5*total)/100
        grand_total = total + tax    
           
    except ObjectDoesNotExist:
        pass
    
    address_form = AddressForm()
    address = Addresses.objects.filter(user = request.user, is_active = True).order_by('-is_default')

    order = Order()
    order.user = request.user
    order.tax = tax
    order.order_total = grand_total
    order.ip = request.META.get('REMOTE_ADDR')
    order.save()
    
    current_datetime = datetime.datetime.now()
    current_year = current_datetime.strftime("%Y")
    current_month = current_datetime.strftime("%m")
    current_day = current_datetime.strftime("%d")
    current_hour = current_datetime.strftime("%H")
    current_minute = current_datetime.strftime("%M")
    concatenated_datetime = current_year + current_month + current_day + current_hour + current_minute
    
    order_number = 'BM-ORD'+concatenated_datetime+str(order.pk)
    order.order_id = order_number
    order.save()

    context = {
        'order_id' : order.order_id,
        'total': total,
        'qty' : quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total' : grand_total,
        'address' : address,
        'address_form' : address_form,
        
    }
    return render(request,'store_templates/checkout.html',context)