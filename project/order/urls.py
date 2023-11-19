from django.urls import path
from . import views


urlpatterns = [
    path('order-summary/',views.order_summary, name='order_summary'),
    path('place-order/',views.place_order, name='place_order'),
    
    
    
]