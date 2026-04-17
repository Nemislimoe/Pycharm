from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('profile/', views.profile, name='profile'),
    path('contact/', views.contact, name='contact'),
]
