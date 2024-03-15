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
from order.models import Order,OrderProduct
import itertools
# from django.http import HttpResponse

# Create your views here.

User = get_user_model

def home(request, cat_slug=None):
    
    categories = Category.objects.filter(is_active = True)
    products = Product.objects.filter(is_available = True)
    product_variants = ProductVariant.objects.select_related('product').prefetch_related('attribute').filter(is_active = True)

    order_products = OrderProduct.objects.filter(is_ordered=True).order_by('-created_at')
    variants = ProductVariant.objects.filter(is_active = True)
    sale_data = {str(variant.get_product_name()): 0 for variant in variants }

            
    for order_product in order_products:
        key = str(order_product.variant.get_product_name())
        if sale_data[key]:
            sale_data[key] += order_product.quantity
        else:
            sale_data[key] = order_product.quantity
    
    sale_data = dict(itertools.islice({key: value for key, value in sorted(sale_data.items(), key=lambda item: item[1], reverse = True)}.items(), 5))

    print(sale_data)




    if request.user.is_authenticated:
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
    else:
        wishlist_products = []
    
    if cat_slug:
        try:
            category = Category.objects.get(slug = cat_slug)
            if not category.parent_cat:
                sub_categories = [i for i in categories if i.parent_cat == category]
                
                sub_product_variants = product_variants.filter(product__category__in = sub_categories)
                main_product_variants = product_variants.filter(product__category = category)
                
                product_variants = sub_product_variants.union(main_product_variants)

            else:
                sub_categories = [i for i in categories if i.parent_cat == category]
                if sub_categories:
                    sub_product_variants = product_variants.filter(product__category__in = sub_categories)
                    main_product_variants = product_variants.filter(product__category = category)
                    product_variants = sub_product_variants.union(main_product_variants)
                else:
                    product_variants = product_variants.filter(product__category = category)

        except Exception as e:
            print(e)
    
    context = {
        'sales_data' : sale_data,
        'categories': categories,
        'products' : products,
        'product_variants' : product_variants[:8],
        'wishlist_products': wishlist_products
        
    }
    
    return render(request,'store_templates/index.html',context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def shop(request, cat_slug = None):

    categories = Category.objects.filter(is_active = True)
    price_min = request.GET.get('price-min')
    price_max = request.GET.get('price-max')
    sort_by = request. GET.get('sort')
    name = request.GET.get('new')
    
    product_variants = ProductVariant.objects.all().filter(is_active = True).order_by('-created_date').select_related('product').prefetch_related('attribute')
    
    paginator = Paginator(product_variants,6)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    
    if 'keyword' in request.GET:

        keyword = request.GET['keyword']
        if keyword:
            product_variants = product_variants.filter(Q(product__description__icontains=keyword) | Q(product_variant_slug__icontains = keyword) | Q(product__product_name__icontains = keyword) | Q(product__category__category_name__icontains = keyword))
            # product_variants_count = product_variants.count()
        paginator = Paginator(product_variants,6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)

    if cat_slug:
        try:
            category = Category.objects.get(slug = cat_slug)
            # product_variants = product_variants.filter(product__category=category)
            
            if not category.parent_cat:
                sub_categories = [i for i in categories if i.parent_cat == category]
                
                sub_product_variants = product_variants.filter(product__category__in = sub_categories)
                main_product_variants = product_variants.filter(product__category = category)
                
                product_variants = sub_product_variants.union(main_product_variants)

                paginator = Paginator(product_variants,6)
                page = request.GET.get('page')
                paged_products = paginator.get_page(page)

            else:
                sub_categories = [i for i in categories if i.parent_cat == category]
                if sub_categories:
                    sub_product_variants = product_variants.filter(product__category__in = sub_categories)
                    main_product_variants = product_variants.filter(product__category = category)
                    product_variants = sub_product_variants.union(main_product_variants)
                    paginator = Paginator(product_variants,6)
                    page = request.GET.get('page')
                    paged_products = paginator.get_page(page)
                
                else:
                    product_variants = product_variants.filter(product__category = category)
                    paginator = Paginator(product_variants,6)
                    page = request.GET.get('page')
                    paged_products = paginator.get_page(page)

        except Exception as e:
            print(e)


    #wishlist
    if request.user.is_authenticated:

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
    else:
        wishlist_products = []



    #price filter
    if price_max and price_min:
        paged_products = product_variants.filter(sale_price__lte=price_max, sale_price__gte=price_min)

    elif price_min:
        
        paged_products = product_variants.filter(sale_price__gte=price_min)
    elif price_max:
        paged_products = product_variants.filter(sale_price__lte=price_max)

    #price sort
    if sort_by == "Low-to-High":
        paged_products = product_variants.order_by('sale_price')
    elif sort_by == "High-to-Low":
        paged_products = product_variants.order_by('-sale_price')

    #Sort by new
    if name == 'New':
        paged_products = product_variants.order_by('-created_date')


        
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





