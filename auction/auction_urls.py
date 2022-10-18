from django.urls import path

from . import views

urlpatterns = [
    path('index', views.index, name='index'),
    path('sell', views.sell, name='sell'),
    path('buy', views.buy, name='buy'),
    path('user_login', views.user_login, name='user_login'),
    path('logout', views.logout, name='logout'),
    path('add_product/', views.add_product, name='add_product'),
    path('display_prod/', views.display_prod, name='display_prod'),
    path('make_bid/', views.make_bid, name='make_bid'),
    path('check_your_bids/', views.check_your_bids, name='check_your_bids'),
    path('remove_bid/', views.remove_bid, name='remove_bid'),   
]