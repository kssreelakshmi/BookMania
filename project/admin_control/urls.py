from django.urls import path
from . import views 


urlpatterns = [
    path('', views.admin_home, name="admin_home"),
    path('admin-login/', views.admin_login, name="admin_login"),
    path('admin-logout/', views.admin_logout, name="admin_logout"),
    path('user-management/all-users/', views.all_users, name="all_users"),
    path('user-management/create-user/', views.create_user, name="create_user"),
    path('user-management/update-user/<int:user_id>', views.update_user, name="update_user"),
    path('user-control/<int:user_id>', views.user_control, name="user_control"),
    
    #category management
    path('category-management/all-category/',views.all_category, name="all_category"),
    path('category-control/<slug:cat_slug>', views.category_control, name="category_control"),
    path('category-control/update-category/<slug:cat_slug>', views.update_category, name="update_category"),
    path('category-control/create-category/', views.create_category, name="create_category"),
    
    #product mangement
    path('product-management/all-products/', views.all_products, name="all_products"),
    path('product-management/all-products/product-control/<str:slug>/', views.product_control, name="product_control"),
    path('product-management/create-product/', views.create_product, name="create_product"),
    path('product-management/product-update/<str:slug>/', views.product_update, name="product_update"),
    path('product-management/product-variant-create/<str:slug>/', views.create_product_variant, name="create_product_variant"),
    path('product-management/product-variant-update/<str:product_variant_slug>/', views.product_variant_update, name="product_variant_update"),
    path('product-management/delete-product-variant/<str:product_variant_slug>/', views.delete_product_variant, name="delete_product_variant"),
    
    path('product-management/product-variant-update/additional-product-images/<str:product_variant_slug>/', views.product_variant_update, name="product_variant_update_ajax"),


# Publication management
    path('publication-management/all-publication/', views.all_publication, name="all_publication"),
    path('publication-management/publication-control/<int:id>', views.publication_control, name="publication_control"),
    path('publication-management/publication-update/<int:id>', views.update_publication, name="update_publication"),
    path('publication-management/publication-create/', views.create_publication, name="create_publication"),
    
    # Order management
    path('order-management/all-orders', views.all_orders, name="all_orders"),
    path('order-management/order-details/<str:order_id>/', views.update_order, name="order_details"),


    
    
    



]