from django.shortcuts import render
from store.models import Product,ProductVariant,Publication,Attribute,AttributeValue,Author, AdditionalProductImages
from category.models import Category
from django.contrib.auth import get_user_model
from cart.models import Cart_item
from cart.views import _cart_id
from django.http import HttpResponse

# Create your views here.

User = get_user_model

def home(request, cat_slug=None):
    
    categories = Category.objects.filter(is_active = True)
    product_variants = ProductVariant.objects.select_related('product').prefetch_related('attribute').filter(is_active = True)[:8]
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
                    
                
        
        except Exception as e:
            print(e)
    
    context = {
        'categories': categories,
        'product_variants' : product_variants,
        
    }
    
    return render(request,'store_templates/index.html',context)


def shop(request, cat_slug = None):
    categories = Category.objects.filter(is_active = True)
    
    if cat_slug:
        category = Category.objects.get(slug = cat_slug)
        product_variants = ProductVariant.objects.filter(product__category=category, is_active = True)
        
    else:
        product_variants = ProductVariant.objects.all().filter(is_active = True)
        
    context = {
        'product_variants': product_variants,
        'categories': categories,
    }
    return render(request, 'store_templates/shop.html', context)


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


def search(request):
    return HttpResponse("search page")