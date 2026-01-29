from django.urls import path, include
from rest_framework.routers import DefaultRouter
from products import views, api_views

# API Router
router = DefaultRouter()
router.register(r'api/kategori', api_views.KategoriViewSet)
router.register(r'api/status', api_views.StatusViewSet)
router.register(r'api/produk', api_views.ProdukViewSet)

# URL Patterns
urlpatterns = [
    # Web views
    path('', views.produk_list, name='produk_list'),
    path('produk/<int:pk>/', views.produk_detail, name='produk_detail'),
    path('produk/tambah/', views.produk_create, name='produk_create'),
    path('produk/<int:pk>/edit/', views.produk_update, name='produk_update'),
    path('produk/<int:pk>/hapus/', views.produk_delete, name='produk_delete'),
    
    # API routes
    path('', include(router.urls)),
]