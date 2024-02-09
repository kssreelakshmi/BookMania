from django.shortcuts import render
import json
from .models import Wishlist, WishlistItem
from store.models import ProductVariant 
from django.http import Http404, JsonResponse
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse, reverse_lazy
# Create your views here.

def wishlist(request):
    wishlist = Wishlist.objects.get(user=request.user)
    wishlist_items = WishlistItem.objects.filter(wishlist = wishlist)
    wishlist_count = wishlist_items.count()
    print(wishlist_count)
    paginator = Paginator(wishlist_items,6)
    page = request.GET.get('page')
    paged_wishlist = paginator.get_page(page)


    context = {
        'wishlists':paged_wishlist,
        'wishlist_count':wishlist_count
    }
    return render(request,'store_templates/wishlist.html',context)


def update_wishlist(request):
    try:
        wishlist = Wishlist.objects.get(user=request.user)
    except Exception as e:
        print(e)

    wishlist_items = WishlistItem.objects.filter(wishlist = wishlist)
    contents = []
    
    for item in wishlist_items:
        contents.append(item.product_variant)

    is_ajax =  request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST' and is_ajax:

        newdata = json.load(request)
        try:
            variant = ProductVariant.objects.get(id = int(newdata.get('product_id')))
        except Exception as e:

            print(e)
        if variant in contents:
            try:
                WishlistItem.objects.get(product_variant = variant).delete()
            except Exception as e:
                print(e)
            
            return JsonResponse({
                'status': 'removed',
                'path': reverse('wishlist')

            })
        else:
            WishlistItem.objects.create(wishlist = wishlist, product_variant = variant)
            return JsonResponse({
                'status': 'added',
            })

    else:
         raise Http404