from django.shortcuts import render,redirect
from store.models import Product,ProductVariant,Publication,Attribute,AttributeValue,Author, AdditionalProductImages
from category.models import Category
from django.contrib.auth import get_user_model
from cart.models import Cart_item
from wishlist.models import Wishlist, WishlistItem
from cart.views import _cart_id
from django.db.models import Q
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.views.decorators.cache import cache_control
# from django.http import HttpResponse

# Create your views here.

User = get_user_model

def home(request, cat_slug=None):
    
    categories = Category.objects.filter(is_active = True)
    products = Product.objects.filter(is_available = True)
    product_variants = ProductVariant.objects.select_related('product').prefetch_related('attribute').filter(is_active = True)[:8]
    wishlist_exists = Wishlist.objects.filter(user = request.user).exists()
    if wishlist_exists:
        try:
            wishlist = Wishlist.objects.get(user = request.user)
        except Exception as e:
            pass
        wishlist_items = WishlistItem.objects.filter(wishlist = wishlist)
        wishlist_products = []
        for item in wishlist_items:
            wishlist_products.append(item.product_variant)
   
    if cat_slug:
        try:
            category = Category.objects.get(slug = cat_slug)
            if not category.parent_cat:
                sub_categories = [i for i in categories if i.parent_cat == category]
                
                sub_product_variants = product_variants.filter(product__category__in = sub_categories)
                main_product_variants = product_variants.filter(product__category = category)
                
                product_variants = sub_product_variants.union(main_product_variants)[:8]

            else:
                sub_categories = [i for i in categories if i.parent_cat == category]
                if sub_categories:
                    sub_product_variants = product_variants.filter(product__category__in = sub_categories)
                    main_product_variants = product_variants.filter(product__category = category)
                    product_variants = sub_product_variants.union(main_product_variants)[:8]
                else:
                    product_variants = product_variants.filter(product__category = category)[:8]
            print(sub_categories)        

        except Exception as e:
            print(e)
    
    context = {
        'categories': categories,
        'products' : products,
        'product_variants' : product_variants,
        'wishlist_products': wishlist_products
        
    }
    
    return render(request,'store_templates/index.html',context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def shop(request, cat_slug = None):
    categories = Category.objects.filter(is_active = True)
    price_min = request.GET.get('price-min')
    price_max = request.GET.get('price-max')
    
    if 'keyword' in request.GET:

        keyword = request.GET['keyword']
        if keyword:
            product_variants = ProductVariant.objects.order_by('-created_date').filter(Q(product__description__icontains=keyword) | Q(product_variant_slug__icontains = keyword) | Q(product__product_name__icontains = keyword) | Q(product__category__category_name__icontains = keyword)).filter(is_active=True)
            # product_variants_count = product_variants.count()
        paginator = Paginator(product_variants,6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)

    elif cat_slug:
        category = Category.objects.get(slug = cat_slug)
        product_variants = ProductVariant.objects.filter(product__category=category, is_active = True).order_by('-created_date').select_related('product').prefetch_related('attribute')
        
        paginator = Paginator(product_variants,6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)

    else:
        product_variants = ProductVariant.objects.all().filter(is_active = True).order_by('-created_date').select_related('product').prefetch_related('attribute')
        
        paginator = Paginator(product_variants,6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)

    #wishlist
    wishlist_exists = Wishlist.objects.filter(user = request.user).exists()
    if wishlist_exists:
        try:
            wishlist = Wishlist.objects.get(user = request.user)
        except Exception as e:
            pass
        wishlist_items = WishlistItem.objects.filter(wishlist = wishlist)
        wishlist_products = []
        for item in wishlist_items:
            wishlist_products.append(item.product_variant)
         

    # price filter
    if price_min:
        product_variants = product_variants.filter(sale_price__gte=price_min)
    if price_max:
        product_variants = product_variants.filter(sale_price__lte=price_max)  

    attribute_names = [key for key in request.GET.keys() if key not in ['query','price-min','price-max','RATING']]

    for attribute_name in attribute_names:
        attribute_values = request.GET.getlist(attribute_name)
        if attribute_values:
            product_variants=product_variants.filter(attribute__attribute_value__in=attribute_values)
    
          
        
    context = {
        'product_variants': paged_products,
        'categories': categories,
        'price_min':price_min,
        'price_max':price_max,
        'wishlist_products': wishlist_products,
    }
    return render(request, 'store_templates/shop.html', context)

    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def product_variant_detail(request,cat_slug,product_variant_slug):
    try:
        single_product = ProductVariant.objects.select_related('product').prefetch_related('attribute','additional_product_images').get(product__category__slug=cat_slug, product_variant_slug=product_variant_slug, is_active=True)
        in_cart = Cart_item.objects.filter(cart__cart_id = _cart_id(request),product = single_product).exists()
        add_images = AdditionalProductImages.objects.filter(product_variant = single_product)
        product_variants = ProductVariant.objects.filter(product=single_product.product,is_active=True)
        product_variants_count=product_variants.count()
       
    except Exception as e:
        raise e
        
    context = {
        'single_product': single_product,
        'add_images': add_images,
        'product_variants': product_variants,
        'product_variants_count': product_variants_count,
        'in_cart' : in_cart,
    }
    return render(request,'store_templates/product_variant_detail.html', context)





