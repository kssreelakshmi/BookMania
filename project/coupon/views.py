from django.shortcuts import render
from cart.models import Cart_item
from .models import Coupon
from order.models import Order
from django.http import JsonResponse
from datetime import date
import json


def coupon_control(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == "POST" and is_ajax:
        current_user = request.user
        data = json.load(request)
            
        action = data.get('action')
        coupon_code = data.get('coupon_code')
        order_number = data.get('order_id')
        order = Order.objects.get(is_ordered = False, order_id = order_number)
        # Update the order status based on the order_number and selected_option
        coupon = Coupon.objects.filter(coupon_code__iexact=coupon_code, is_active=True, expire_date__gt=date.today())
        if not coupon.exists():
            return JsonResponse({"status": "error", "message": "Invalid Coupon Or Coupon Expired"})
        
        total_incl_tax = order.order_total
        total = total_incl_tax - order.tax
        
        if action == 'apply_coupon':

            if coupon[0].minimum_amount > total:
                return JsonResponse({
                    "status": "error",
                    "message": "Minimum Purchase amount "+str(coupon[0].minimum_amount)
                    })
            coupon_discount = (total * coupon[0].discount_percentage)/100

            total -= coupon_discount
            tax = (5 * total) / 100
            order.order_total = total + tax
            order.tax = tax
            order.coupon = coupon[0]
            order.coupon_discount = coupon_discount
            order.save()
            
            return JsonResponse({
                "status": "coupon_applied",
                "message": "Coupon Applied",
                "coupon_code": coupon[0].coupon_code,
                'coupon_discount': coupon_discount,
                'tax': order.tax,
                "grand_total": order.order_total,
                })
        
        elif action == 'remove_coupon':
            total += order.coupon_discount
            tax = (5 * total) / 100
            order.order_total = total + tax
            order.tax = tax
            order.coupon = None
            order.coupon_discount = 0
            order.save()
            
            return JsonResponse({
                "status": "coupon_removed",
                "message": "Coupon Removed",
                "coupon_code": coupon[0].coupon_code,
                'coupon_discount': 0,
                'tax': order.tax,
                "grand_total": order.order_total,
                })

        else:
            # Return a JSON response indicating an invalid request
            return JsonResponse({"status": "error", "message": "Invalid request"})
