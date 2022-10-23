from django.contrib import admin
from django.urls import path, include
from amazon.views import *

urlpatterns = [
    path('', home, name="home"),
    path('signup', sign_up, name="signup"),
    path('login', login, name="login"),
    path('signup_auth', signup_auth, name="verify"),
    path("logout", logout, name="logout"),
    path('products', prods, name="products"),
    path('prod', single_prod, name="s_product"),
    path('prod/to_cart', modify_cart, name="to_Cart"),
    path('user_data', get_global_data, name="data"),
    path('my_cart', cart_data, name="cart"),
    path('from_cart', remove_item, name='r_item'),
    path('get_query_data', get_query_data, name="s_results"),
    path('my_prods', search_prods, name="s_initialization"),
    path('profile', profile, name="profile"),
]
