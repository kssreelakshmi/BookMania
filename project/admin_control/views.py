from django.shortcuts import render,redirect
from django.urls import reverse
from accounts.forms import UserSignupForm
from category.forms import CategoryForm
from store.forms import ProductForm,ProductVariantForm,PublicationForm
from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import cache_control
from category.models import Category
from store.models import Product,ProductVariant,Attribute,AttributeValue,Author,AdditionalProductImages,Publication
from order.models import Order, OrderProduct, Payment, PaymentMethod
from order.forms import OrderStatusForm
from django.db.models import OuterRef, Subquery
from django.http import JsonResponse
import json

# Create your views here.
User = get_user_model()

def check_isadmin(view_func, redirect_url="admin_login"):
    
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_admin:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "You need to be logged in as an admin to access this page")
        else:
            messages.error(request, "You need to be logged in as an admin to access this page")

        redirect_url_ = reverse(redirect_url) + '?next=' + request.path
        return redirect(redirect_url_)

    return wrapper

@check_isadmin
@login_required(login_url='admin_login')
def admin_home(request):
    
    return render(request,'admin-dashboard/admin_home.html')

# @check_isadmin
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

@login_required(login_url='admin_login')
# @check_isadmin
def all_users(request):
    users= User.objects.all().exclude(is_admin = True)
    context = {
        'users': users
    }
    return render(request,'admin-dashboard/account_management/all_users.html',context)

# @check_isadmin
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
            print(form.errors)
            messages.error(request,form.errors)
            return render(request,'admin-dashboard/account_management/update_user.html',{'form': form})

    context = {
        'form': form,
        }
    return render(request,'admin-dashboard/account_management/update_user.html',context)

# @check_isadmin
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
            messages.success(request, "User Created ")
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

@login_required(login_url='admin_login')
def all_category(request):
    
    categories = Category.objects.all().order_by('id')
    context = {
        'all_categories': categories,
    }
    return render(request, 'admin-dashboard/category_management/all_category.html', context)


@login_required(login_url='admin_login')
def category_control(request, cat_slug):
    try:
        category = Category.objects.get(slug = cat_slug)
    except Exception as e:
        print(e)
    
    category.is_active = not category.is_active
    category.save()
    return redirect('all_category')


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


@login_required(login_url='admin_login')
def all_products(request):
    products= Product.objects.annotate(
    image=Subquery(
        ProductVariant.objects.filter(product_id=OuterRef('pk')).values('thumbnail_image')[:1]
    ))
    
    context = {
        'products': products
    }
    return render(request,'admin-dashboard/product_management/all_product.html',context)

@login_required(login_url='admin_login')
def product_control(request,slug):
    product = Product.objects.get(slug=slug)
    product.is_available = not product.is_available
    product.save()
    
    return redirect('all_products')


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
    
@login_required(login_url='admin_login')
def product_variant_update(request,product_variant_slug):
    
    try:
        product_variant= ProductVariant.objects.get(product_variant_slug=product_variant_slug)
   
    except ProductVariant.DoesNotExist:
        return redirect('all_products')
    
    variant_form = ProductVariantForm(instance=product_variant)
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
                return JsonResponse({"status": "success",
                                     'new_image': additional_image.image.url,})
                
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
        if variant_form.is_valid():
            variant = variant_form.save()
            
            messages.success(request, "Variant Updated")
            return redirect('product_update', product_variant.product_variant_slug)
        else:
            messages.error(request, variant_form.errors)
            context = {
                'variant_form': variant_form,
                'product_variant_slug':product_variant_slug,
                'product_variant': product_variant,
                'current_additional_images': current_additional_product_images,
            }
            
            return render(request,'admin-dashboard/product_management/variant_update.html')
    context = {
        'variant_form': variant_form,
        'product_variant_slug': product_variant_slug,
        'product_variant': product_variant,
        'current_additional_images': current_additional_product_images,
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
    
    context = {
        'publications': publications
    }
    return render(request,'admin-dashboard/publication_management/all_publication.html',context)


@login_required(login_url='admin_login')
def publication_control(request, id):
    print('reached here')
    try:
        publication = Publication.objects.get(id=id)
    except Exception as e:
        print(e)
    
    publication.is_active = not publication.is_active
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

    
@login_required(login_url='admin_login')
def all_orders(request):
    order_status = request.GET.get('status')
    
    if order_status:
        orders = Order.objects.filter(order_status__icontains=order_status).order_by('-created_at')
    else: 
        orders = Order.objects.all().order_by('-created_at')
    context = {
        'orders': orders
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
        print("selected option is  :",selected_option)

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
    context = {
        'order': order,
        'order_products': order_products,
        'total': total,
        'payment': payment,
        'form': form,
    }
    return render(request, 'admin-dashboard/order_management/order_details.html',context)