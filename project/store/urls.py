from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="user_home" ),
    path('products/<slug:cat_slug>', views.home, name="products_by_category" ),
    path('store/product-detail/<slug:cat_slug>/<slug:product_variant_slug>/', views.product_variant_detail, name="product_variant_detail" ),
    path('store/all-products/', views.shop, name="shop" ),
    # category filter
    path('store/all-products/by-category/<slug:cat_slug>/', views.shop, name="shop_by_cat" ),
    path('search', views.search, name="search" ),

]
