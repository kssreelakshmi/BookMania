from django.shortcuts import render,redirect,get_object_or_404
from .forms import UserSignupForm,AddressForm
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.sites.shortcuts import get_current_site
from .models import Addresses 
from cart.models import Cart,Cart_item
from cart.views import _cart_id
from django.contrib.auth import login, logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.core.mail import EmailMessage
import requests

# Create your views here.

User = get_user_model()

def user_signup(request):
    if request.user.is_authenticated:
        return redirect('user_home')
    
    if request.user.is_authenticated and request.user.is_admin:
        return redirect('admin_home')  # need to change to admin home
    
    
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        form = UserSignupForm(request.POST)
        for field in ['is_active', 'is_admin', 'is_staff']:
            form.fields.pop(field, None)
        
        if password != confirm_password:
            messages.error(request,'Password mismatch')
            return render(request,'base/user_side/signup.html',{'form': form})
        
        if form.is_valid():

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = User.objects.create_user(
                first_name = first_name,
                last_name =last_name,
                username = username,
                email = email,
                password = password,
                phone_number = phone_number
            )

            # Send email confirmation
            current_site = get_current_site(request)
            subject = 'Activate your account'
            data = {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            }
            message = render_to_string('base/user_side/verification/account-activation.html', data)
            to_email = email
            send_email = EmailMessage(subject, message,to=[to_email])
            send_email.content_subtype = 'html'
            send_email.send()
            
            messages.success(request,'Account created successfully. Email activation link has been send to your Email, Verify to continue..')
            return redirect('user_login')
        else:
            return render(request,'base/user_side/signup.html',{'form': form})
    form = UserSignupForm()
    context = {
        'form': form,
    }
    return render(request,'base/user_side/signup.html',context)



def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Email verification completed. You can now login')
        return redirect('user_login')
    else:
        return HttpResponseBadRequest('Activation link is invalid!')



def user_login(request):
    if request.user.is_authenticated and request.user.is_admin:
        return redirect('admin_home')
    
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        if not email:
            messages.warning(request,'Email is required !')
            return redirect('user_login')
        if not password:
            messages.warning(request,'Password is required !')
            return redirect('user_login')
        check_if_user_exists = User.objects.filter(email=email).exists()
        if check_if_user_exists:
            user = authenticate(email=email, password=password)
        
            if user is not None:
                try:
                    cart = Cart.objects.get(cart_id = _cart_id(request))
                    is_cartitem = Cart_item.objects.get(cart=cart)
                   
                    if is_cartitem:
                        cart_items = Cart_item.objects.filter(cart=cart)
                        user_cart_items = Cart_item.objects.filter(user=user)
                        
                        for cart_item in cart_items:
                            for user_cart_item in user_cart_items:
                                if cart_item.product == user_cart_item.product:
                                    cart_item.quantity += user_cart_item.quantity
                                    cart_item.save()
                                    user_cart_item.delete()

                            cart_item.user = user
                            cart_item.save()
                            print(cart_item.user)
                                                    
                except Exception as e:
                    print(e)
                    
                login(request,user)
                messages.success(request,'You are now logged in')

                url = request.META.get('HTTP_REFERER')
                try:
                    query = requests.utils.urlparse(url).query
                    params = dict(x.split('=') for x in query.split('&'))
                    if 'next' in params:
                        nextPage = params['next']
                        return redirect(nextPage)
                except:
                    return redirect('user_home')
            else:
                messages.error(request,'Invaid Password !')
                return redirect('user_login')
        else:
            messages.error(request,'Invalid Email ID !')
            return redirect('user_login')
            
    
    return render(request,'base/user_side/user_login.html')


def forgot_password(request):
    return render(request,'base/user_side/forgot_password.html')


@login_required (login_url='user_login')
def user_logout(request):
    logout(request)
    messages.success(request,'you are logged out')
    return redirect('user_home')


@login_required (login_url='user_login')
def user_dashboard(request):
    return render(request,'base/user_side/user_dashboard.html')



def my_address(request):
    current_user = request.user
    address_form = AddressForm()
    addresses = Addresses.objects.filter(user=current_user, is_active=True).order_by('-is_default')
    
    context = {
        'address_form' : address_form,
        'addresses' : addresses,
    }
    
    return render(request,'base/user_side/my_address.html',context)


def add_address(request,source):
    
    if request.method == 'POST':
        
        address_form = AddressForm(request.POST)
        if address_form.is_valid:
            address = address_form.save(commit = False)
            address.user = request.user
            address.is_default = True
            address.save()
            if source == 'cart_checkout':
                return redirect('cart_checkout')
            else:
                return redirect('my_address')
        else:
            context ={
                'address_form' : address_form,
            }
            return render(request,'base/user_side/my_address.html',context)
 
        
def default_address(request, id):
    try:  
        address = Addresses.objects.get(id=id)
        address.is_default = True
        address.save()
        return redirect('my_address')
    except Addresses.DoesNotExist:
        return redirect('my_address')
            
            
def delete_address(request,id):
    
    try:
        
        address = Addresses.objects.get(id=id)
        address.is_active = False
        address.save()
        return redirect('my_address')                
    
    except Addresses.DoesNotExist:
        return redirect('my_address')                