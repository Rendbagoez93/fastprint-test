from django.contrib import admin
from django.utils.html import format_html
from .models import Kategori, Status, Produk


@admin.register(Kategori)
class KategoriAdmin(admin.ModelAdmin):
    list_display = ['id_kategori', 'nama_kategori', 'produk_count']
    search_fields = ['nama_kategori']
    
    def produk_count(self, obj):
        count = obj.produk_set.count()
        return format_html('<span style="color: blue;">{}</span>', count)
    produk_count.short_description = 'Jumlah Produk'


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['id_status', 'nama_status', 'produk_count']
    search_fields = ['nama_status']
    
    def produk_count(self, obj):
        count = obj.produk_set.count()
        return format_html('<span style="color: blue;">{}</span>', count)
    produk_count.short_description = 'Jumlah Produk'


@admin.register(Produk)
class ProdukAdmin(admin.ModelAdmin):
    list_display = ['id_produk', 'nama_produk', 'harga_formatted', 'kategori', 'status']
    list_filter = ['status', 'kategori']
    search_fields = ['nama_produk']
    list_select_related = ['kategori', 'status']
    
    def harga_formatted(self, obj):
        return format_html('Rp {:,.2f}', obj.harga)
    harga_formatted.short_description = 'Harga'
    harga_formatted.admin_order_field = 'harga'

