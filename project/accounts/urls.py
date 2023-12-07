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
    
    
    path('my-account/', views.user_dashboard, name='user_dashboard'),
    path('my-account/user-profile-update/', views.update_user_profile, name='update_user_profile'),
    path('my-account/profile-update/', views.update_profile, name='update_profile'),
    path('my-account/order-history', views.order_history, name='order_hidtory'),
    path('my-account/myaddress', views.my_address, name='my_address'),
    path('my-account/add-address/<str:source>/', views.add_address, name='add_address'),
    path('my-account/default-address', views.default_address, name= 'default_address'),
    path('my-account/delete-address', views.delete_address, name='delete_address'),
    
]