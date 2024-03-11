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
    path('sales-report', views.sales_report, name="sales_report"),

    path("api/dashboard/data/sales", views.DashboardSalesData.as_view(), name="api-dashboard-sales"),
    path("api/dashboard/data/product2sales", views.DashboardProductVsOrderData.as_view(), name="api-dashboard-productvsorder"),
    
    
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
    path('product-management/all-attribute/', views.all_attributes, name='all_attributes'),
    path('product-management/attribute-control/<int:id>/', views.attribute_control, name="attribute_control"),
    path('product-management/create-attribute/', views.create_attribute, name='create_attribute'),
    path('product-management/update-attribute/<int:id>/', views.update_attribute, name='update_attribute'),

    path('product-management/all-attribute-values', views.all_attribute_values, name='all_attribute_values'),
    path('product-management/attribute-value-control/<int:id>/', views.attribute_value_control, name="attribute_value_control"),
    path('product-management/add-attribute-values/', views.add_attribute_values, name='add_attribute_values'),
    path('product-management/update-attribute-values/<int:id>/', views.update_attribute_values, name='update_attribute_values'),

# Publication management
    path('publication-management/all-publication',views.all_publication, name="all_publication"),
    path('publication-management/publication-control/<int:id>/', views.publication_control, name="publication_control"),
    path('publication-management/publication-update/<int:id>/', views.update_publication, name="update_publication"),
    path('publication-management/publication-create/', views.create_publication, name="create_publication"),

# Author Management
    path('author-management/all-authors',views.all_authors,name='all_authors'),
    path('author-management/author-control/<int:id>/',views.author_control,name='author_control'),
    path('author-management/add-authors/',views.add_authors,name='add_authors'),
    path('author-management/update-authors/<int:id>/',views.update_author,name='update_author'),
    
# Order management
    path('order-management/all-orders', views.all_orders, name="all_orders"),
    path('order-management/order-details/<str:order_id>/', views.update_order, name="order_details"),
    path('order-management/order-cancel-or-return/', views.order_handle, name="order_cancel_return"),


#coupon management   
    path('coupon-management/all-coupons', views.all_coupon, name="all_coupon"),
    path('coupon-management/create-coupon/', views.create_coupon, name="create_coupon"),
    path('coupon-management/coupon-update/<int:id>/', views.coupon_update, name="coupon_update"),
    path('coupon-management/delete-coupon//<int:id>/', views.delete_coupon, name="delete_coupon"),
    
    



]