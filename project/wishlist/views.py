from django.shortcuts import render
import json
from .models import Wishlist
from store.models import ProductVariant 
from django.http import Http404, JsonResponse
# Create your views here.

def wishlist(request):
    
    return render(request,'store_templates/wishlist.html')

def update_wishlist(request):
    is_ajax =  request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == 'POST' and is_ajax:
        newdata = json.load(request)
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            variant = ProductVariant.objects.get(id = int(newdata.product_id))
        except Exception as e:
            print(e)
        if newdata.action == 'add':
            wishlist.product_variant = variant
            wishlist.save()
            return JsonResponse({
                'status': 'added',
            })
        else:
            wishlist.delete()
            return JsonResponse({
                'status': 'removed',
            })
    else:
         raise Http404