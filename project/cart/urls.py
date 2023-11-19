from django.urls import path
from . import views



urlpatterns = [
    path('',views.cart, name='cart'),
    path('add-to-cart/<int:product_id>',views.Add_to_cart, name='add_to_cart'),
    path('update-cart/',views.Add_to_cart, name='update_cart_ajax'),
    path('remove-cart-item/<int:product_id>',views.Remove_cart_item, name='remove_cart_item'),
    path('checkout/',views.Cart_checkout, name='cart_checkout'),
]