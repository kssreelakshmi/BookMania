from django.shortcuts import render,redirect
from django.urls import reverse
from accounts.forms import UserSignupForm
from category.forms import CategoryForm
from store.forms import ProductForm,ProductVariantForm,PublicationForm,AuthorForm,CreateAttributeForm,CreateAttributeValueForm
from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib import messages
from django.core.mail import EmailMessage
from category.models import Category
from coupon.models import Coupon
from accounts.models import Account
from django.contrib.sites.shortcuts import get_current_site
from store.models import Product,ProductVariant,Attribute,AttributeValue,Author,AdditionalProductImages,Publication
from order.models import Order, OrderProduct, Payment, PaymentMethod,Invoice
from order.forms import OrderStatusForm
from django.db.models import OuterRef, Subquery
from admin_control.forms import CouponForm
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.http import JsonResponse
from django.db.models import Count, F, Sum, Avg
from io import BytesIO
from django.template.loader import get_template,render_to_string
from xhtml2pdf import pisa
from django.http import HttpResponse
import json
import datetime
import itertools
import calendar
import pytz
from django.utils import timezone
from datetime import timedelta, date
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.
User = get_user_model()

def check_isadmin(view_func, redirect_url="admin_login"):
  """
  Decorator that restricts access to views to authenticated admins.

  Redirects non-authenticated users to the specified redirect URL.
  """

  @login_required
  def wrapper(request, *args, **kwargs):
    if request.user.is_admin:
      return view_func(request, *args, **kwargs)
    else:
      messages.error(request, "You need to be logged in as an admin to access this page")
      redirect_url_ = reverse(redirect_url) + '?next=' + request.path
      return redirect(redirect_url_)

  return wrapper


@check_isadmin
@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_home(request):

    orders = Order.objects.filter(is_ordered=True).order_by('-created_at')
    orders_count =orders.count()
    order_products = OrderProduct.objects.filter(is_ordered=True)
    user = Account.objects.filter(is_active = True).exclude(is_admin = True)
    products = ProductVariant.objects.filter(is_active = True)
    category = Category.objects.filter(is_active = True).count()
    total_revenue = orders.aggregate(total_revenue=Sum('order_total'))
    extracted_total_revenue = total_revenue['total_revenue']
    delivered_oders = orders.filter(order_status="Delivered")
    coupons = Coupon.objects.filter(is_active = True)
    coupon_count= coupons.count()
    
   
    context = {
            'coupons ' : coupons ,
            'coupon_count ' : coupon_count ,
            'order_products': order_products,
            'orders':orders[:8],
            'orders_count' : orders_count,
            'products' : products.count(),
            'category' : category,
            'total_revenue': extracted_total_revenue,
            'users' : user.count(),
            'delivered_oders' : delivered_oders,
    }
    return render(request,'admin-dashboard/admin_home.html',context)

class DashboardSalesData(APIView):
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, format=None):    
        print('reached efrerferf3ef')
        total_orders_count  = OrderProduct.objects.filter(is_ordered=True).count()
        new_orders_count  = OrderProduct.objects.filter(is_ordered=True,order_status='New').count()
        cancelled_orders_count  = OrderProduct.objects.filter(is_ordered=True,order_status__in=["Cancelled"]).count()
        returned_orders_count  = OrderProduct.objects.filter(is_ordered=True,order_status=['Returned']).count()
        cancellation_requested_count  = OrderProduct.objects.filter(is_ordered=True,order_status__in=["Cancelled"]).count()
        return__requested_count  = OrderProduct.objects.filter(is_ordered=True,order_status=['Returned']).count()
        delivered_orders_count  = OrderProduct.objects.filter(is_ordered=True,order_status='Delivered').count()
        data = {
                'status':'success',
                'data':{
                    'Total Orders':total_orders_count,
                    'New Orders':new_orders_count,
                    'cancelled Orders':cancelled_orders_count,
                    'Returned Orders':returned_orders_count,
                    'Cancellation Requested' : cancellation_requested_count,
                    'Return Requested' : return__requested_count,
                    'Delivered Orders':delivered_orders_count,
                    }    
            }
        return Response(data)
    

class DashboardProductVsOrderData(APIView):
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, format=None):
        
        order_products = OrderProduct.objects.filter(is_ordered=True).order_by('-created_at')
        variants = ProductVariant.objects.filter(is_active = True)
        sale_data = {str(variant.sku_id): 0 for variant in variants }

            
        for order_product in order_products:
            key = str(order_product.variant.sku_id)
            if sale_data[key]:
                sale_data[key] += order_product.quantity
            else:
                sale_data[key] = order_product.quantity
        
        sale_data = dict(itertools.islice({key: value for key, value in sorted(sale_data.items(), key=lambda item: item[1], reverse = True)}.items(), 5))

        print(sale_data)
    
        data = {
            'status': 'success',
            'data': sale_data
        }
        return Response(data, content_type="application/json")

@check_isadmin
@login_required(login_url='admin_login')
def sales_report(request):
    if request.GET:
        start_date = request.GET['start-date']
        end_date = request.GET['end-date']
       
        if not end_date:
            end_date = datetime.date.today()
        
        order_products = OrderProduct.objects.filter(is_ordered=True, created_at__date__range=(start_date, end_date)).order_by('-created_at')
    else:
        order_products = OrderProduct.objects.filter(is_ordered=True).order_by('-created_at')


    variants = ProductVariant.objects.filter(is_active = True)
    stock = {}
    for variant in variants:
        stock[variant.get_product_name()] = {
            'product_name' : variant.product.product_name,
            'total_stock' : variant.stock,
            'sale_price' : int(variant.sale_price)
            }

    # stock data is in stock dictionary
    sale_data = {variant.get_product_name(): 0 for variant in variants }

    for order_product in order_products:
        if sale_data[order_product.variant.get_product_name()]:
            sale_data[order_product.variant.get_product_name()] += order_product.quantity
        else:
            sale_data[order_product.variant.get_product_name()] = order_product.quantity
            
    for data in stock:
        stock[data]['sold_quantity'] = sale_data[data]
        stock[data]['total_revenue'] = stock[data]['sold_quantity'] * stock[data]['sale_price']

    

    orders = Order.objects.filter(is_ordered=True).order_by('-created_at')
    orders_count = orders.count()
    product_variants = ProductVariant.objects.filter(is_active = True)
    user = Account.objects.filter(is_active = True).exclude(is_admin = True)
    total_revenue = orders.aggregate(total_revenue=Sum('order_total'))
    extracted_total_revenue = total_revenue['total_revenue']    

    cancelled_order_total = OrderProduct.objects.filter(is_ordered=True, order_status='Cancelled').aggregate(cancelled_order_total=Sum(F('product_price') * F('quantity')))
    cancelled_amount = cancelled_order_total['cancelled_order_total']
    returned_order_total = OrderProduct.objects.filter(is_ordered=True, order_status='Returned').aggregate(returned_order_total=Sum(F('product_price') * F('quantity')))
    returned_amount = returned_order_total['returned_order_total']
    final_amount = extracted_total_revenue - (returned_amount+cancelled_amount)

    context = {
        'variant_sale_data' : stock,
        'product_variants': product_variants,
        'orders_count' : orders_count,
        'users' : user.count(),
        'revenue' : extracted_total_revenue,
        'final_amount': final_amount,
    }


    return render(request,'admin-dashboard/sales_report.html',context)


@check_isadmin
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_login(request):
    if request.user.is_authenticated and request.user.is_admin:
        return redirect('admin_home')
    
    if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')
            
            if not email:
                messages.warning(request,'Email is required !')
                return redirect('admin_login')
            
            if not password:
                messages.warning(request,'Password is required !')
                return redirect('admin_login')
            
            check_if_user_exists = User.objects.filter(email=email).exists()
            
            if check_if_user_exists:
                user = authenticate(email=email, password=password)
        
                if user is not None:
                    
                    if not user.is_admin:
                        messages.success(request,'You are not allowed to access this page ')
                        return redirect('user_home')
                    
                    login(request,user)
                    messages.success(request,'You are now logged in')
                    return redirect('admin_home')
                else:
                    
                    messages.error(request,'Invaid Password !')
                    return redirect('admin_login')
            else:
                messages.error(request,'Invalid Email ID !')
                return redirect('admin_login')
        
    return render(request, 'admin-dashboard/admin_login.html')

@check_isadmin
@login_required(login_url='admin_login')
def all_users(request):
    users= User.objects.all().exclude(is_admin = True)
    paginator = Paginator(users,5)
    page = request.GET.get('page')
    paged_users = paginator.get_page(page)
    context = {
        'users': paged_users
    }
    return render(request,'admin-dashboard/account_management/all_users.html',context)

@check_isadmin
@login_required(login_url='admin_login')
def user_control(request, user_id):
    if not request.user.is_admin:
        return redirect('user_home')
    try:
        user = User.objects.get(id = user_id)
    except Exception as e:
        print(e)
    
    user.is_active = not user.is_active
    user.save()
    return redirect('all_users')


@check_isadmin
@login_required(login_url='admin_login')
def update_user(request,user_id):
    user = User.objects.get(id = user_id)
    form = UserSignupForm(instance = user)
    form.fields.pop('password', None)
    
    if request.method == 'POST':
        
        form = UserSignupForm(request.POST,instance = user)
        form.fields.pop('password', None)
        if form.is_valid():
            form.save()
            
            messages.success(request, 'User edited successfully')
            return redirect('all_users')
        else:
            messages.error(request,form.errors)
            return render(request,'admin-dashboard/account_management/update_user.html',{'form': form})

    context = {
        'form': form,
        }
    return render(request,'admin-dashboard/account_management/update_user.html',context)

@check_isadmin
@login_required(login_url='admin_login')
def create_user(request):
        
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password =request.POST.get('confirm_password')

        form = UserSignupForm(request.POST)
        if password != confirm_password:
            messages.error(request,'Password mismatch')
            return render(request,'admin-dashboard/account_management/create_user.html',{ 'form':form})
        
        if form.is_valid():
            user = form.save(commit = False)
            user.set_password(password)
            
            user.save()
            messages.success(request, "User Created")
            return redirect('all_users')
        
        else:
            return render(request,'admin-dashboard/account_management/create_user.html',{ 'form':form})
        
    form = UserSignupForm()
    context = {
        'form' : form,
    }
            
    return render(request,'admin-dashboard/account_management/create_user.html',context)

def admin_logout(request):
    logout(request)
    messages.success(request,'you are logged out')
    return redirect('admin_login')


# category control

@check_isadmin
@login_required(login_url='admin_login')
def all_category(request):
    categories = Category.objects.all().order_by('id')
    paginator = Paginator(categories,10)
    page = request.GET.get('page')
    paged_categories = paginator.get_page(page)
    
    context = {
        'all_categories': paged_categories,
    }
    return render(request, 'admin-dashboard/category_management/all_category.html', context)

@check_isadmin

@login_required(login_url='admin_login')
def category_control(request, cat_slug):
    try:
        category = Category.objects.get(slug = cat_slug)
    except Exception as e:
        print(e)

    products = Product.objects.filter(category = category)
    if category.is_active:
        category.is_active = False

        for product in products:
            product.is_available = False
            product.save()
            for variant in product.productvariant_set.all():
                variant.is_active = False
                variant.save()

    else:
        category.is_active = True

        for product in products:
            product.is_available = True
            product.save()
            for variant in product.productvariant_set.all():
                variant.is_active = True
                variant.save()
    category.save()
    return redirect('all_category')

@check_isadmin

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='admin_login')
# @check_isadmin
def update_category(request, cat_slug):
    try:
        category = Category.objects.get(slug = cat_slug)
        
    except Exception as e:
        print(e)
    form = CategoryForm(instance = category)
    
    if request.method == 'POST':    
        form = CategoryForm(request.POST, instance=category)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated")
            return redirect('all_category')
        else:
            messages.error(request, form.errors)
            return render(request, 'admin-dashboard/category_management/category-update.html', context)

    context = {
        'form': form
        }
    return render(request, 'admin-dashboard/category_management/category-update.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='admin_login')
# @check_isadmin
def create_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)
                
        if form.is_valid():
            form.save()
            messages.success(request, "Category created")
            return redirect('all_category')
        else:
            context = {
                'form': form
            }
            return render(request, 'admin-dashboard/category_management/category-create.html', context)
    else:
        form = CategoryForm()
        context = {
            'form': form,
        }
    return render(request, 'admin-dashboard/category_management/category-create.html', context)

@check_isadmin
@login_required(login_url='admin_login')
def all_products(request):
    products= Product.objects.annotate(
    image=Subquery(
        ProductVariant.objects.filter(product_id=OuterRef('pk')).values('thumbnail_image')[:1]
    ))
   
    
    paginator = Paginator(products,10)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    context = {
        'products': paged_products,
    }
    return render(request,'admin-dashboard/product_management/all_product.html',context)

@check_isadmin
@login_required(login_url='admin_login')
def product_control(request,slug):
    product = Product.objects.get(slug=slug)
    product.is_available = not product.is_available
    product.save()
    
    return redirect('all_products')

@check_isadmin

@login_required(login_url='admin_login')
def create_product(request):
    
    product_form = ProductForm()
    variant_form = ProductVariantForm()
    variant_form.fields.pop('attribute',None)
    attributes = Attribute.objects.prefetch_related('attributevalue_set').filter(is_active=True)
    
    attribute_dict = {}
    for attribute in attributes:
        attribute_values = attribute.attributevalue_set.filter(is_active= True)
        attribute_dict[attribute.attribute_name] = attribute_values
    attribute_values_count =attributes.count()
    
    
    if request.method == 'POST':
        product_form = ProductForm(request.POST)
        variant_form = ProductVariantForm(request.POST,request.FILES)
        variant_form.fields.pop('attribute',None)        
        attribute_ids =[]
        
        for i in range(1,attribute_values_count+1):
            attribute_value_id = request.POST.get('attributes_'+str(i))
            if attribute_value_id != 'None':
                attribute_ids.append(int(attribute_value_id)) 
        
        if product_form.is_valid() and variant_form.is_valid():
            product = product_form.save()
            variant = variant_form.save(commit=False)
            variant.thumbnail_image = request.FILES.get('thumbnail_image')
            variant.product = product
            variant.save()
            variant.attribute.set(attribute_ids)
            additional_images = request.FILES.getlist('additional_images')
            for image in additional_images:
                AdditionalProductImages.objects.create(product_variant=variant, image=image)
                
            messages.success(request,'product added')
            return redirect('all_products')
        
        else:
            
            messages.error(request,variant_form.errors)
            
            context = {
                'product_form': product_form,
                'variant_form' : variant_form,
                'attribute_dict' : attribute_dict,
            }       
            return render(request,'admin-dashboard/product_management/create_product.html',context)
    else:    
      
        context = {
                'product_form': product_form,
                'variant_form' : variant_form,
                'attribute_dict' : attribute_dict,
            }          
    
    return render(request,'admin-dashboard/product_management/create_product.html',context)

@check_isadmin

@login_required(login_url='admin_login')
def product_update(request,slug):
    
    product = Product.objects.get(slug = slug)
    product_variants = ProductVariant.objects.filter(product = product)
    form = ProductForm(instance = product)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated")
            return redirect('all_products')
            
        else:
            messages.error(request, form.errors)
            return redirect('product_update', slug)
    
    context = {
        'form': form,
        'product_variants':product_variants, 
        'slug': slug,
        }
    return render(request,'admin-dashboard/product_management/update_product.html', context)

@check_isadmin

@login_required(login_url='admin_login')
def create_product_variant(request,slug):
    try:
        product = Product.objects.get(slug=slug)
    except Product.DoesNotExist:
        return redirect('all_products')
    
    variant_form = ProductVariantForm()
    variant_form.fields.pop('attribute',None)
    attributes = Attribute.objects.prefetch_related('attributevalue_set').filter(is_active=True)
    
    attribute_dict = {}
    for attribute in attributes:
        attribute_values = attribute.attributevalue_set.filter(is_active= True)
        attribute_dict[attribute.attribute_name] = attribute_values
    attribute_values_count =attributes.count()
    
    if request.method == 'POST':

        variant_form = ProductVariantForm(request.POST,request.FILES)
        variant_form.fields.pop('attribute',None)        
        attribute_ids =[]
    
        for i in range(1,attribute_values_count+1):
            attribute_value_id = request.POST.get('attributes_'+str(i))
            if attribute_value_id != 'None':
                attribute_ids.append(int(attribute_value_id)) 
        
        thumbnail_image = request.FILES.get('thumbnail_image')        
        if variant_form.is_valid():
            variant = variant_form.save(commit=False)
            variant.thumbnail_image = request.FILES.get('thumbnail_image')
            variant.product = product
            variant.thumbnail_image = thumbnail_image
            variant.save()
            variant.attribute.set(attribute_ids)
            variant.save()
            additional_images = request.FILES.getlist('additional_images')
            for image in additional_images:
                AdditionalProductImages.objects.create(product_variant=variant, image=image)    
           
            messages.success(request,'product added')
            return redirect('all_products')
        
        else:
            
            messages.error(request,variant_form.errors)
            return redirect('create_product_variant',slug)
            
    context = {
        
        'variant_form' : variant_form,
        'slug' : slug,
        'product' : product,
        'attribute_dict' : attribute_dict,
    }   
    return render(request,'admin-dashboard/product_management/create_product_variant.html',context)

@check_isadmin

@login_required(login_url='admin_login')
def product_variant_update(request, product_variant_slug):
    
    try:
        product_variant= ProductVariant.objects.get(product_variant_slug=product_variant_slug)
   
    except ProductVariant.DoesNotExist:
        return redirect('all_products')
    
    
    variant_form = ProductVariantForm(instance=product_variant)

    attributes = Attribute.objects.prefetch_related('attributevalue_set').filter(is_active=True)
    variant_attributes_list = []
    variant_attributes = product_variant.attribute.all()

    for value in variant_attributes:
        variant_attributes_list.append(value.attribute_value)

    
    attribute_dict = {}
    for attribute in attributes:
        attribute_values = attribute.attributevalue_set.filter(is_active= True)
        attribute_dict[attribute.attribute_name] = attribute_values
    attribute_values_count =attributes.count()
    


    current_additional_product_images = product_variant.additional_product_images.all()
    
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if  request.method == 'POST' and is_ajax:
        image = request.FILES['file']
        image_id = request.POST['image_id']
        
        if image_id == 'thumbnail':
            image_id = None
        if image and image_id:
            
            try: 
                additional_image = AdditionalProductImages.objects.get(id=image_id)
                additional_image.image = image
                additional_image.save()
                return JsonResponse({
                                     "status": "success",
                                     'new_image': additional_image.image.url,
                                     })
                
            except Exception as e:
                print(e)
        elif image and (not image_id):
            
            try:
                product_variant.thumbnail_image = image
                product_variant.save()
                
                return JsonResponse({
                    'status': 'success',
                    'new_image': product_variant.thumbnail_image.url,
                    })
            except Exception as e :
                print(e)
        else:
            return JsonResponse({"status": "error", "message": "image send error !"})
        
    if request.method == 'POST':
        variant_form = ProductVariantForm(request.POST,instance=product_variant)
        variant_form.fields.pop('attribute',None)        
        attribute_ids =[]
    
        for i in range(1,attribute_values_count+1):
            attribute_value_id = request.POST.get('attributes_'+str(i))
            if attribute_value_id != 'None':
                attribute_ids.append(int(attribute_value_id)) 

        if variant_form.is_valid():
            variant = variant_form.save()
            variant.attribute.set(attribute_ids)
            variant.save()
            
            messages.success(request, "Variant Updated")
            return redirect('product_update', product_variant.product_variant_slug)
        else:
            messages.error(request, 'Invalid credentials !')
            return redirect('product_variant_update', product_variant_slug)
        
    context = {
        'variant_form': variant_form,
        'product_variant_slug': product_variant_slug,
        'product_variant': product_variant,
        'current_additional_images': current_additional_product_images,
        'attribute_dict' : attribute_dict,
        'variant_attributes_list':variant_attributes_list,
        }
    return render(request,'admin-dashboard/product_management/variant_update.html',context)

@login_required(login_url='admin_login')
def delete_product_variant(request,product_variant_slug):
    try:
        product_variant = ProductVariant.objects.get(product_variant_slug=product_variant_slug)
    except ProductVariant.DoesNotExist:
        return redirect('all_products')
    except ValueError:
        return redirect('all_products')
    product_variant.delete()
    messages.error(request, "Variant Deleted")
    return redirect('all_products')


@login_required(login_url='admin_login')
def all_publication(request):
    publications = Publication.objects.all().order_by('-created_date')
    paginator = Paginator(publications,10)
    page = request.GET.get('page')
    paged_publications = paginator.get_page(page)
    context = {
        'publications': paged_publications,
    }
    return render(request,'admin-dashboard/publication_management/all_publication.html',context)


@login_required(login_url='admin_login')
def publication_control(request, id):
    try:
        publication = Publication.objects.get(id=id)
    except Exception as e:
        print(e)
    
    products = Product.objects.filter(publication = publication)
    if publication.is_active:
        publication.is_active = False

        for product in products:
            product.is_available = False
            product.save()
            for variant in product.productvariant_set.all():
                variant.is_active = False
                variant.save()

    else:
        publication.is_active = True

        for product in products:
            product.is_available = True
            product.save()
            for variant in product.productvariant_set.all():
                variant.is_active = True
                variant.save()
   
    publication.save()
    return redirect('all_publication')

@login_required(login_url='admin_login')
def create_publication(request):
    
    if request.method == 'POST':    
        form = PublicationForm(request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Publication updated")
            return redirect('all_publication')
        else:
            messages.error(request, form.errors)
            return redirect('create_publication')

    form = PublicationForm()
    context = {
        'form': form
        }
    return render(request, 'admin-dashboard/publication_management/create_publication.html', context)


@login_required(login_url='admin_login')
def update_publication(request, id):
    try:
        publication = Publication.objects.get(id=id)
        
    except Exception as e:
        print(e)

    form = PublicationForm(instance = publication)
    
    if request.method == 'POST':    
        form = PublicationForm(request.POST, instance=publication)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Publication updated")
            return redirect('all_publication')
        else:
            messages.error(request, form.errors)
            return render(request, 'admin-dashboard/publication_management/update_publication.html', context)

    context = {
        'form': form
        }
    return render(request, 'admin-dashboard/publication_management/update_publication.html', context)

def all_authors(request):
    authors = Author.objects.all().order_by('-author_created_at')
    paginator = Paginator(authors,10)
    page = request.GET.get('page')
    paged_authors = paginator.get_page(page)
    context = {
        'authors' : paged_authors,
    }
    return render(request,'admin-dashboard/author_management/all_authors.html',context)

def author_control(request,id):
    try:
        author = Author.objects.get(id = id)
    except Exception as e:
        print(e)
    
    products = Product.objects.filter(author = author)
    if author.is_active:
        author.is_active = False

        for product in products:
            product.is_available = False
            product.save()
            for variant in product.productvariant_set.all():
                variant.is_active = False
                variant.save()

    else:
        author.is_active = True

        for product in products:
            product.is_available = True
            product.save()
            for variant in product.productvariant_set.all():
                variant.is_active = True
                variant.save()

    author.save()
    return redirect('all_authors')
    
def add_authors(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Publication updated")
            return redirect('all_authors')
        else:
            messages.error(request, form.errors)
            return redirect('add_authors')
    else:
        form = AuthorForm()
        context = {
            'form': form,
        }  
    return render(request,'admin-dashboard/author_management/add_author.html',context)

def update_author(request,id):
    try:
        author = Author.objects.get(id=id)
        
    except Exception as e:
        print(e)

    form = AuthorForm(instance = author)
    
    if request.method == 'POST':    
        form = AuthorForm(request.POST, instance=author)
        if form.is_valid():
            form.save()
            messages.success(request, "Author updated")
            return redirect('all_author')
        else:
            messages.error(request, form.errors)
            return redirect('update_author')
    form = AuthorForm(instance = author)
    context={
        'form' :form,
    }
    return render(request,'admin-dashboard/author_management/update_author.html',context)

@login_required(login_url='admin_login')
def all_orders(request):
    order_status = request.GET.get('status')
    
    if order_status:
        order_status = order_status.replace("-", " ")
        orders = Order.objects.filter(order_status__icontains=order_status).order_by('-created_at')
    else: 
        orders = Order.objects.all().order_by('-created_at')

    paginator = Paginator(orders,10)
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)
    order = Order()
    choices = order.ORDER_STATUS_CHOICES

    order_status_choices = [choice[0].replace(' ', '-') for choice in choices]

    context = {
        'orders': paged_orders,
        'order_status_choices' : order_status_choices
    }
    return render(request, 'admin-dashboard/order_management/all_orders.html',context)

@login_required(login_url='admin_login')
def update_order(request, order_id):
    try:
        order = Order.objects.get(order_id = order_id)
    except Exception as e:
        messages.error(request, 'order not found')
        return redirect('all_orders')

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.method == "POST" and is_ajax:
        data = json.load(request)
        selected_option = data.get('selected_option')
        order.order_status = selected_option
        order.save()
        return JsonResponse({"status": "success", "selected_option": selected_option})


    order_products = OrderProduct.objects.filter(order = order)
    total = 0
    for order_product in order_products:
        total += order_product.product_price * order_product.quantity

    try:
        payment = Payment.objects.filter(payment_id = order.payment.payment_id)[0]
    except:
        payment = None
    form = OrderStatusForm(instance = order)

    print(order.is_ordered)
    if order.is_ordered:
        invoice = Invoice.objects.filter(order=order).first()

    context = {

        'invoice' :invoice,
        'order': order,
        'order_products': order_products,
        'total': total,
        'payment': payment,
        'form': form,
    }
    return render(request, 'admin-dashboard/order_management/order_details.html',context)




def order_handle(request):
    data = json.load(request)
    # order_product_id = request.GET.get('order_product_id')
    try:
        order_product = OrderProduct.objects.get(id=data.get('order_product_id'))
    except Exception as e:
        print(e)

    if order_product.order_status == 'Cancellation Requested':
        if data.get('operation') == 'accept':
            order_product.order_status = 'Cancelled'
            order_product.variant.stock += 1
            order_product.variant.save()
            order_product.save()

            user = order_product.user
            email = user.email
            print(user)
            current_site = get_current_site(request)
            mail_subject = 'Cancellation Successful'
            data = {
            'user': user,
            'domain': current_site,
            'order_product' : order_product,
            }
            message = render_to_string ('base/admin_side/cancellation.html',data)
            sendNotifyMail(email, message, mail_subject)
            return JsonResponse({
                'status' : 'success',
                'message': 'Reason validated, product cancelled from order',
                'additional_message': 'Cancellation approved'
            })
        
        elif data.get('operation') == 'reject':
            order_product.order_status = 'Cancellation Rejected'
            order_product.save()
            
            user = order_product.user
            email = user.email
            current_site = get_current_site(request)
            mail_subject = 'Cancellation Rejected!'
            data = {
            'user': user,
            'domain': current_site,
            'order_product' : order_product,
            }
            message = render_to_string ('base/admin_side/cancellation_rejected.html',data)
            sendNotifyMail(email, message, mail_subject)

            return JsonResponse({
                'status' : 'success',
                'message': 'Cancellation request has been rejected',
                'additional_message': 'Rejected'
            })


    elif order_product.order_status == 'Return Requested':
        if data.get('operation') == 'accept':
            order_product.order_status = 'Returned'
            order_product.variant.stock += 1
            order_product.variant.save()
            order_product.save()

            user = order_product.user
            email = user.email
            current_site = get_current_site(request)
            mail_subject = 'Return Successful'
            data = {
            'user': user,
            'domain': current_site,
            'order_product' : order_product,
            }
            message = render_to_string ('base/admin_side/return.html',data)
            sendNotifyMail(email, message, mail_subject)

            return JsonResponse({
                'status' : 'success',
                'message': 'Reason validated',
                'additional_message': 'product return approved'
            })
        elif data.get('operation') == 'reject':
            order_product.order_status = 'Return Rejected'
            order_product.save()

            user = order_product.user
            email = user.email
            current_site = get_current_site(request)
            mail_subject = 'Return Request Rejected'
            data = {
            'user': user,
            'domain': current_site,
            'order_product' : order_product,
            }
            message = render_to_string ('base/admin_side/return_rejected.html',data)
            sendNotifyMail(email, message, mail_subject)

            return JsonResponse({
                'status' : 'success',
                'message': 'Return request has been rejected',
                'additional_message': 'Rejected'
            })

    return redirect('order_details')

def sendNotifyMail(email, message, mail_subject):
    to_email = email
    send_email = EmailMessage(mail_subject,message,to=[to_email])
    send_email.content_subtype = 'html'
    send_email.send()
    return




def all_attributes(request):
    attribute =Attribute.objects.all()
    paginator = Paginator(attribute,10)
    page = request.GET.get('page')
    paged_attribute = paginator.get_page(page)
    context = {
        'attribute' : paged_attribute,
    }
    return render(request,'admin-dashboard/product_management/all_attributes.html',context)

def attribute_control(request,id):
    try:
        attribute = Attribute.objects.get(id = id)
    except Exception as e:
        print(e)
    
    attribute.is_active = not attribute.is_active
    attribute.save()
    return redirect('all_attributes')

def create_attribute(request):
    if request.method == 'POST':
        attribute_form = CreateAttributeForm(request.POST)
        if attribute_form.is_valid():
            attribute_form.save()
            messages.success(request, "Attribute added")
            return redirect('all_attributes')
        else:
            messages.error(request, attribute_form.errors)
            return redirect('create_attribute')
    attribute_form = CreateAttributeForm()
    context = {
        'attribute_form': attribute_form,
    }  
    return render(request,'admin-dashboard/product_management/create_attribute.html',context)

def update_attribute(request,id):
    try:
        attribute = Attribute.objects.get(id=id)
    except Exception as e:
        print(e)

    attribute_form = CreateAttributeForm(instance = attribute)
    
    if request.method == 'POST':    
        attribute_form = CreateAttributeForm(request.POST, instance=attribute)
        
        if attribute_form.is_valid():
            attribute_form.save()
            messages.success(request, "Attribute updated")
            return redirect('all_attributes')
        else:
            messages.error(request, attribute_form.errors)
            return redirect('update_attribute')
    attribute_form = CreateAttributeForm(instance = attribute)
    context = {
        'attribute_form' : attribute_form,
    }
    return render(request,'admin-dashboard/product_management/update_attributes.html',context)

def all_attribute_values(request):
    attributevalue = AttributeValue.objects.all()
    paginator = Paginator(attributevalue,10)
    page = request.GET.get('page')
    paged_attributevalue = paginator.get_page(page)
    context = {
        'attributevalue' : paged_attributevalue,
    }
    return render(request,'admin-dashboard/product_management/all_attribute_values.html',context)

def attribute_value_control(request,id):
    try:
        attribute_value = AttributeValue.objects.get(id = id)
    except Exception as e:
        print(e)
    
    attribute_value.is_active = not attribute_value.is_active
    attribute_value.save()
    return redirect('all_attribute_values')

def add_attribute_values(request):
    if request.method == 'POST':
        attribute_value_form = CreateAttributeValueForm(request.POST)
        if attribute_value_form.is_valid():

            attribute_value_form.save()
            messages.success(request, "Attribute value added")
            return redirect('all_attribute_values')
        else:

            messages.error(request, attribute_value_form.errors)
            return redirect('create_attribute_value')
        
    attribute_value_form = CreateAttributeValueForm()
    context = {
        'attribute_value_form': attribute_value_form,
    }  
    return render(request,'admin-dashboard/product_management/create_attribute_value.html',context)

def update_attribute_values(request,id):
    try:
        attribute_value = AttributeValue.objects.get(id=id)
    except Exception as e :
        print(e)

    attribute_value_form = CreateAttributeValueForm(instance = attribute_value)
    if request.method == 'POST':
        attribute_value_form = CreateAttributeValueForm(request.POST,instance=attribute_value)

        if attribute_value_form.is_valid():
            attribute_value_form.save()
            messages.success(request, "Attribute value updated")
            return redirect('all_attribute values')
        else:
            messages.error(request, attribute_value_form.errors)
            return redirect('update_attribute_values')
        
    attribute_value_form = CreateAttributeValueForm(instance=attribute_value)
    context = {
        'attribute_value_form' : attribute_value_form,
        }
    return render(request,'admin-dashboard/product_management/update_attribute_values.html',context)


def all_coupon(request):
    coupons = Coupon.objects.all()
    paginator = Paginator(coupons,10)
    page = request.GET.get('page')
    paged_coupons = paginator.get_page(page)

    context= {
        'coupons' :paged_coupons, 
    }
    return render(request,'admin-dashboard/coupon_management/available_coupons.html',context)


def create_coupon(request):

    if request.method =='POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Coupon added successsfully')
            return redirect('all_coupon')
        else:

            messages.error(request, form.errors)
            return redirect('create_coupon')
        
    form = CouponForm()
    context = {
        'form': form,
    }  
    return render(request,'admin-dashboard/coupon_management/create_coupon.html',context)

def coupon_update(request,id):
    try:
        coupon = Coupon.objects.get(id=id)
    except Exception as e:
            print(e)

    form = CouponForm(instance = coupon)
        
    if request.method == 'POST':    
        form = CouponForm(request.POST, instance=coupon)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Coupon updated")
            return redirect('all_coupon')
        else:
            messages.error(request, form.errors)
            return redirect('update_attribute')
    form = CouponForm(instance = coupon)
    context = {
        'form' : form,
    }
    return render(request,'admin-dashboard/coupon_management/coupon_update.html',context)


def delete_coupon(request,id):
    try:
        coupon = Coupon.objects.get(id=id)
    except Coupon.DoesNotExist:
        return redirect('all_coupon')
    except ValueError:
        return redirect('all_coupon')
    coupon.delete()
    messages.error(request, "Coupon Deleted")
    return redirect('all_coupon')

