from django.urls import path, include
from . import views

urlpatterns = [
    path('',views.wishlist,name='wishlist'),
    path('wishlist-update/',views.update_wishlist,name='update_wishlist'),

    
]