from django.shortcuts import render,redirect,get_object_or_404
from .forms import UserSignupForm,AddressForm,UserProfilePicForm
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
from django.http import HttpResponseBadRequest, JsonResponse
from django.core.mail import EmailMessage
from accounts.models import UserProfile
import requests, json, random
from django.views.decorators.cache import cache_control
from wishlist.models import Wishlist
# Create your views here.

User = get_user_model()

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_signup(request):
    if request.user.is_authenticated:
        return redirect('user_home')
    
    if request.user.is_authenticated and request.user.is_admin:
        return redirect('admin_home')
    
    
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
                    try:
                        wishlist_exist = Wishlist.objects.filter(user=user).exists()
                        if not wishlist_exist:
                            wishlist = Wishlist.objects.create(user=user)
                    except Exception as e:
                        print (e)
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

def user_login_with_otp(request):
    
    if request.user.is_authenticated:
        return redirect('user_home')
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.method == 'POST' and is_ajax:
        email = json.load(request)
        if not email:
            messages.warning(request,'Email is required !')
            return JsonResponse({
                'status': 'error',
                'message': 'Enter valid email',
            })
        check_if_user_exists = User.objects.filter(email=email).exists()
        if check_if_user_exists:
            user = User.objects.get(email=email)
            if user is not None:
                otp = random.randint(111111, 999999)
                UserProfile.objects.all().delete()
                user_profile = UserProfile.objects.create(user = user)
                user_profile.otp = otp
                user_profile.save()

                subject = 'Login With OTP'
                data = {
                    'user': user,
                    'otp': otp,
                }
                message = render_to_string('base/user_side/verification/email_login_otp.html', data)
                to_email = email
                send_email = EmailMessage(subject, message,to=[to_email])
                send_email.content_subtype = 'html'
                send_email.send()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'OTP is send to your registered email address.',
                    'uid': user_profile.uid,
                })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Enter valid email',
            })
    return render(request,'base/user_side/login_otp.html')


def verify_otp(request, uid):
    try:
        user_profile = UserProfile.objects.get(uid = uid)
    except Exception as e:
        print(e)

    otp = request.GET['otp']        
    print(otp)
    if otp == user_profile.otp:
        login(request, user_profile.user)
        messages.success(request, 'Login successfull !!!')
        return redirect('user_home')
    else:
        messages.error(request, 'Invalid OTP !!!')
        return redirect('user_login_with_otp')
        

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        user_exists = User.objects.filter(email=email).exists()
        if user_exists:
            user = User.objects.get(email__exact=email)
            current_site = get_current_site(request)
            subject = 'Reset Your Password'
            data = {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                }
            message = render_to_string('base/user_side/verification/change_password.html', data)
            to_email = email
            send_email = EmailMessage(subject, message,to=[to_email])
            send_email.content_subtype = 'html'
            send_email.send()
            messages.success(request,'Reset password link is send to your registered email. kindly check your email')
            return redirect('user_login')
        else:
            messages.error(request, "Account doesn't exist,Please sign up")
            return redirect('user_home')
    return render(request,'base/user_side/forgot_password.html')


def reset_password_verify(request,uid64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uid64).decode())
        user = User.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.success(request,'Password resetting completed.')
        return redirect('user_login')
    else:
        messages.error(request,'Invalid link')
        return redirect('forgot_password')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            uid = request.session.get('uid')
            try:
                user = User.objects.get(pk=uid)
                user.set_password(password)
                user.save()
                messages.success(request,"Password Resetting Completed")
                return redirect('user_login')
            except User.DoesNotExist:
                messages.error(request, "Error")    
                return redirect('user_login')
        else:
            messages.error(request, "Password Not Match")
            return redirect('reset-password')
            
    return render(request,'base/user_side/reset.html')


@login_required (login_url='user_login')
def user_logout(request):
    logout(request)
    messages.success(request,'you are logged out')
    return redirect('user_home')


@login_required (login_url='user_login')
def user_dashboard(request):
    
    return render(request,'base/user_side/user_dashboard.html')


def update_user_profile(request):
    if request.method == 'POST':
        profile = UserProfilePicForm(request.POST,request.FILES,instance=request.user)
        if profile.is_valid():
            profile.save()
        return redirect('user_dashboard')    
    else:    
        return redirect('user_dashboard')
            
def update_profile(request):

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == 'POST' and is_ajax:
        data =json.load(request)
        field = data['field']
        value = data['value']
        try:
            user = request.GET.get(user = request.user.id)
            field_tracing = {
                'first_name': 'first_name',
                'last_name' : 'last_name',
                'username' : 'username'
            }
            if field in field_tracing:
                setattr(user,field_tracing[field],value)
                user.save()
                return JsonResponse({'status' : 'success'})
            else:
                return JsonResponse({
                    'status' : 'error',
                    'message' : 'Contact Admin'
                })
        except:
                return JsonResponse({
                    'status' : 'error',
                    'message' : 'Invalid Request'
                })
        
def email_change(request):
    pass

def order_history(request):
    return render(request,'base/user_side/order_history.html')


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
    
    