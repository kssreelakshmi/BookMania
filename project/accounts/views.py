from django.shortcuts import render,redirect,get_object_or_404
from .forms import UserSignupForm,AddressForm,UserProfilePicForm, AddressCountryForm
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
from order.models import Order,OrderProduct,Payment,PaymentMethod
import requests, json, random
from django.views.decorators.cache import cache_control
from wishlist.models import Wishlist
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django_countries.fields import CountryField
from django.contrib.auth.hashers import check_password
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse
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
                    is_cartitem = Cart_item.objects.filter(cart=cart).exists()
                   
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
                    pass
                try:
                    wishlist_exist = Wishlist.objects.filter(user=user).exists()
                    if not wishlist_exist:
                        wishlist = Wishlist.objects.create(user=user)   
                        print(wishlist,'ffgduhasidoiopisoiSOIOisIHDUGSAGDSFGYDGSYFGDUFHUHUHS')
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
            user = User.objects.get(id= request.user.id)
            setattr(user,field,value)
            user.save()
            return JsonResponse({
                'status' : 'success'
                })
        except:
            return JsonResponse({
                'status' : 'error',
                'message' : 'Contact Admin'
            })
    else:
        return JsonResponse({
            'status' : 'error',
            'message' : 'Invalid Request'
        })
        
def mobile_number_change(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == 'POST' and is_ajax:
        data =json.load(request)
        get_new_number = data['new_number']

        if (request.user.phone_number == get_new_number):
            return JsonResponse({
                "status" : "error",
                "message" : "Please enter a new mobile number",
            })
        try:
            user = User.objects.get(phone_number=request.user.phone_number)
            email = User.objects.get(email=request.user.email)
            otp = random.randint(100000,999999)
            user_otp,created = UserProfile.objects.update_or_create(user=user,defaults={'otp' :otp})

            subject = 'Mobile Number Change'
            current_site = get_current_site(request)
            data = {
                'user': user,
                'domain': current_site,
                'otp': user_otp.otp,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),

            }
            message = render_to_string('base/user_side/verification/mobile_change.html', data)
            to_email = email
            send_email = EmailMessage(subject, message,to=[to_email])
            send_email.content_subtype = 'html'
            send_email.send()
            
            return JsonResponse({
                "status": "success",
                "message": get_new_number,
                })
        except:
            return JsonResponse({
                "status": "error",
                "message": 'Unable to send OTP , Please check mobile number again'})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request"})
    
def mobile_number_change_verify(request):
    is_ajax = is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == 'POST' and is_ajax:
       data = json.load(request)
       otp = data['otp']
       pass 
    try:
        user_profile = UserProfile.objects.get(uid = request.user.uid)
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


def email_change(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == "POST" and is_ajax:
        data = json.load(request)
        get_new_email = data['new_email']
        
        if (request.user.email == get_new_email):
            return JsonResponse({"status": "error", "message": 'Entered email is same as current email'})
        
        try:
            user = User.objects.get(email = request.user.email)
            print(user)
            otp=random.randint(100000,999999)
            user_otp,created = UserProfile.objects.update_or_create(user=user, defaults={'otp': f'{otp}'})
            current_site = get_current_site(request)
            mail_subject = 'Update your Email address'
            data = {
            'user': user,
            'domain': current_site,
            'otp': user_otp.otp,
            }
            message = render_to_string ('base/user_side/verification/email_change.html',data)
            to_email = get_new_email
            print(to_email)
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            print(send_email)
            send_email.content_subtype = 'html'
            send_email.send() 

            return JsonResponse({
                "status": "success",
                "message": 'Enter Otp To Change'
                })
        except:
            return JsonResponse({
                "status": "error", 
                "message": 'Unable to send mail , Please check mail again'
                })
            
    else:
        return JsonResponse({
            "status": "error", 
            "message": "Invalid request"
            })

def change_email_verify(request):  
    
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == "POST" and is_ajax:
        data = json.load(request)
        get_new_email = data['new_email']
        get_otp = data['otp']
        
        user = User.objects.get(id=request.user.id)
     
        user_otp = UserProfile.objects.filter(user=user,otp=get_otp).exists()
        
        if user_otp:
            user.email = get_new_email
            user.save()
            messages.success(request,"Email ID changed successfully")
            return JsonResponse({
                "status": "success",
                "message": 'OTP OK'
                 })
        else:
            return JsonResponse({
                "status": "error", 
                "message": 'Invalid Otp'})

# def password_change(request):
#     is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
#     if request.method == "POST" and is_ajax:
#         data = json.load(request)
                
#         try:
#             current_password= request.user.password #user's current password
#             current_password_entered= data['old_password']
#             password2= data['password2']

#             matchcheck= check_password(current_password_entered, current_password)
            
#             if matchcheck:
#                 user = User.objects.get(id=request.user.id)
#                 user.set_password(password2)
#                 user.save()  
#                 update_session_auth_hash(request, user)

#                 messages.success(request, "Password Change Successfully")
#                 return JsonResponse({"status": "success"})
#             else:
#                 return JsonResponse({"status": "error","message": "Invalid Old Password"})
        
#         except:
#             return JsonResponse({"status": "error", "message": "Contact Admin"})

#     else:
#         # Return a JSON response indicating an invalid request
#         return JsonResponse({"status": "error", "message": "Invalid request"})
    
def password_change(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == "POST" and is_ajax:
        email = request.user.email
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)
            
            #SEND OTP TO MAIL
            otp=random.randint(1000,9999)
            user_otp,created = UserProfile.objects.update_or_create(user=user, defaults={'otp': f'{otp}'})
            
            current_site = get_current_site(request)
            mail_subject = 'Password Change'
            message = render_to_string ('base/user_side/verification/password_change.html',{
                'user' : user,
                'domain' : current_site,
                'otp':user_otp.otp,
                
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.content_subtype = 'html'
            send_email.send()
            messages.success(request, "Email Has Been Successfully shared , please verify to reset")
            
            redirect_to =redirect('password_change', uid=user_otp.uid)
            redirect_to.set_cookie("can_otp_enter",True,max_age=600)
            redirect_url = reverse('password_change', kwargs={'uid':user_otp.uid})
            print(redirect_url)
            return JsonResponse({"status": "success", "redirect_url": redirect_url})
    else:
        # Return a JSON response indicating an invalid request
        return JsonResponse({"status": "error", "message": "Invalid request"})
    
        
def change_password_with_email(request,uid):  
    if request.method == "POST":
        userOtp=UserProfile.objects.get(uid=uid)     
        if request.COOKIES.get('can_otp_enter')!=None:
            if(userOtp.otp==request.POST['otp']):
               
                user = User.objects.get(id=request.user.id)
                user.set_password(request.POST['password1'])
                user.save()  
                messages.success(request, "Password Changed Successfully")
                return redirect('user-dashboard')      
            else:
                messages.error(request, "Invalid Otp")
                return render(request,'accounts/change_password_with_mail.html')
        else:
            messages.error(request, "2 mins Over ! Time Exceeded")
            return render(request,'accounts/change_password_with_mail.html')
    else:
        return render(request, 'accounts/change_password_with_mail.html')
        



def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('created_at')
    paginator = Paginator(orders,3)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)

    context={
        'orders':paged_products,
    }
    return render(request,'base/user_side/order_history.html', context)

def order_detail(request,order_id):
    try:
        order = Order.objects.get(order_id = order_id)
        products = OrderProduct.objects.filter(order = order)
        sub_total = 0
        tax = 0
        grand_total = 0

        for product in products:
            sub_total += product.variant.sale_price * product.quantity
        tax += (5 * sub_total)/100     
        grand_total += sub_total + tax

    except:
        messages.warning(request,'The details of this order is not available')
        return redirect('order_history')

    context={
        'order':order, 
        'products' : products,
        'payment' : order.payment,
        'sub_total' : sub_total,
        'tax' : tax,
        'grand_total' : grand_total,

    }
    return render(request,'base/user_side/order_details.html',context)

def order_cancel_or_return(request):
    pass

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
        if address_form.is_valid():
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
    else:
        context ={
            'address_form' : address_form,
        }
        return render(request,'base/user_side/my_address.html',context)
 

def get_country_choices():
   return [(code, str(name)) for code, name in CountryField().get_choices()]



def update_address(request):

    if request.method == 'GET':
        id = request.GET.get('id')
        try:
            address = Addresses.objects.get(id = int(id))
        except Exception as e:
            print(e)
            return JsonResponse({
                'status': 'error',
                'message': 'Address not found'
            })
        
        address_form = AddressForm(request.POST, instance = address)
        form_data = model_to_dict(address_form.instance)
        form_data.pop('country')
        form_data['country'] = address.country.name
        print(form_data)

        country_choices = get_country_choices()
        countries = json.dumps(country_choices)
        
        return JsonResponse({
            'formData': form_data,
            'countries': countries
        })
    
        # return JsonResponse({
        #     'id': address.id,
        #     'name': address.name,
        #     'phone_number':address.phone_number,
        #     'addrl1': address.address_line_1,
        #     'addrl2': address.address_line_2,
        #     'city': address.city,
        #     'state': address.state,
        #     'country': address.get_country_display(),
        #     'pincode': address.pincode,
        # })
    elif request.method =='POST':
        
        address_id = request.POST.get('id')
        try:
            address = Addresses.objects.get(id = address_id)
            print(address)
        except Exception as e:
            print(e)

        address_form = AddressForm(request.POST,instance = address)
        if address_form.is_valid():
            new_address = address_form.save()

            return JsonResponse({
                "status" : 'Success',
                'message': 'Address updated successfully'
            })
        else:
            return JsonResponse({
                "name_error": address_form.errors
                })    

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
    
    