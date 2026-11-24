from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),

    path('product/<int:id>/',
         views.product_detail,
         name='product_detail'),

    path('add-to-cart/<int:id>/',
         views.add_to_cart,
         name='add_to_cart'),

    path('cart/',
         views.cart_view,
         name='cart'),

    path('register/', views.register_view, name='register'),

    path('login/', views.login_view, name='login'),

    path('logout/', views.logout_view, name='logout'),

    path('checkout/', views.checkout_view, name='checkout'),

    path(
    'order-success/<int:id>/',
    views.order_success,
    name='order_success'
),

    path('my-orders/', views.my_orders, name='my_orders'),

    path('order-detail/<int:id>/', views.order_detail, name='order_detail'),
]
