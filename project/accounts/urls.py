from django.urls import path
from . import views


urlpatterns = [
    path('signup/', views.user_signup, name='user_signup'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('user-login/', views.user_login, name='user_login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('user-logout/', views.user_logout, name='user_logout'),
    
    
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user/myaddress', views.my_address, name='my_address'),
    path('user/add-address/<str:source>/', views.add_address, name='add_address'),
    path('user/default-address', views.default_address, name= 'default_address'),
    path('user/delete-address', views.delete_address, name='delete_address'),
    
]