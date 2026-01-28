from django.urls import path
from products import views

urlpatterns = [
    path('', views.produk_list, name='produk_list'),
    path('produk/<int:pk>/', views.produk_detail, name='produk_detail'),
    path('produk/tambah/', views.produk_create, name='produk_create'),
    path('produk/<int:pk>/edit/', views.produk_update, name='produk_update'),
    path('produk/<int:pk>/hapus/', views.produk_delete, name='produk_delete'),
]