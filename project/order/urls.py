from django.urls import path
from . import views


urlpatterns = [
    path('order-summary/',views.order_summary, name='order_summary'),
    path('place-order/',views.place_order, name='place_order'),
    path('payment-success/',views.payment_success, name='payment_success'),
    path('payment-failed/',views.payment_failed, name='payment_failed'),
    path('order-completed/',views.order_completed, name='order_completed'),
    
    
    
    
]