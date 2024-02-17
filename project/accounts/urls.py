from django.urls import path
from . import views


urlpatterns = [
    path('signup/', views.user_signup, name='user_signup'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('user-login/', views.user_login, name='user_login'),
    path('user-login-with-otp/', views.user_login_with_otp, name='user_login_with_otp'),
    path('user-login-with-otp/verify/<str:uid>/', views.verify_otp, name='verify_otp'),
    
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path("reset/password/<uidb64>/<token>/", views.reset_password_verify, name="reset_password_verify"),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('user-logout/', views.user_logout, name='user_logout'),
    
    # user account management
    path('my-account/', views.user_dashboard, name='user_dashboard'),
    path('user-profile-update/', views.update_user_profile, name='update_user_profile'),
    path('profile-update/', views.update_profile, name='update_profile'),

    path('mobile-number-change/', views.mobile_number_change, name='mobile_number_change'),
    path('mobile-number-change/verify/', views.mobile_number_change_verify, name='mobile_number_change_verify'),
    path('email-change/', views.email_change, name='email_change'),
    path('email-change/verify', views.email_change, name='change_email_verify'),
    path('password-change/', views.password_change, name='password_change'),


    path('order-history/', views.order_history, name='order_history'),
    path('order-detail/<str:order_id>/', views.order_detail, name='order_detail'),
    path('myaddress/', views.my_address, name='my_address'),
    path('add-address/<str:source>/', views.add_address, name='add_address'),
    path('update-address/',views.update_address,name='update_address'),
    path('default-address/<int:id>/', views.default_address, name= 'default_address'),
    path('delete-address/<int:id>/', views.delete_address, name='delete_address'),



    path('product-cancel-request/',views.product_cancel_request, name='product_cancel_request'),
    path('product-return-request/',views.product_return_request, name='product_return_request'),
    
]