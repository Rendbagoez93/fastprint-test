from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.cache import cache

from products.models import Produk, Status
from products.forms import ProdukForm


def _get_bisa_dijual_status():
    """Get or cache 'bisa dijual' status."""
    status = cache.get('bisa_dijual_status')
    if status is None:
        try:
            status = Status.objects.get(nama_status__iexact='bisa dijual')
            cache.set('bisa_dijual_status', status, 3600)  # Cache for 1 hour
        except Status.DoesNotExist:
            status = None
    return status


def produk_list(request):
    """Display list of products with optional status filter."""
    show_filter = request.GET.get('show', 'bisa_dijual')
    produk_list = Produk.objects.select_related('kategori', 'status')
    
    if show_filter != 'all':
        bisa_dijual_status = _get_bisa_dijual_status()
        if bisa_dijual_status:
            produk_list = produk_list.filter(status=bisa_dijual_status)
            title = 'Daftar Produk - Bisa Dijual'
        else:
            messages.warning(request, 'Status "bisa dijual" tidak ditemukan. Menampilkan semua produk.')
            title = 'Daftar Produk - Semua'
    else:
        title = 'Daftar Produk - Semua'
    
    return render(request, 'products/produk_list.html', {
        'produk_list': produk_list,
        'title': title,
        'show_filter': show_filter,
    })


def produk_detail(request, pk):
    """Display detail of a single product."""
    produk = get_object_or_404(Produk.objects.select_related('kategori', 'status'), pk=pk)
    return render(request, 'products/produk_detail.html', {
        'produk': produk,
        'title': f'Detail Produk - {produk.nama_produk}'
    })


def produk_create(request):
    """Create a new product."""
    if request.method == 'POST':
        form = ProdukForm(request.POST)
        if form.is_valid():
            produk = form.save()
            messages.success(request, f'Produk "{produk.nama_produk}" berhasil ditambahkan!')
            return redirect('produk_list')
    else:
        form = ProdukForm()
    
    return render(request, 'products/produk_form.html', {
        'form': form,
        'title': 'Tambah Produk',
        'action': 'Tambah'
    })


def produk_update(request, pk):
    """Update an existing product."""
    produk = get_object_or_404(Produk, pk=pk)
    
    if request.method == 'POST':
        form = ProdukForm(request.POST, instance=produk)
        if form.is_valid():
            produk = form.save()
            messages.success(request, f'Produk "{produk.nama_produk}" berhasil diperbarui!')
            return redirect('produk_detail', pk=produk.pk)
    else:
        form = ProdukForm(instance=produk)
    
    return render(request, 'products/produk_form.html', {
        'form': form,
        'title': f'Edit Produk - {produk.nama_produk}',
        'action': 'Perbarui',
        'produk': produk
    })


def produk_delete(request, pk):
    """Delete a product."""
    produk = get_object_or_404(Produk, pk=pk)
    
    if request.method == 'POST':
        nama_produk = produk.nama_produk
        produk.delete()
        messages.success(request, f'Produk "{nama_produk}" berhasil dihapus!')
        return redirect('produk_list')
    
    return render(request, 'products/produk_confirm_delete.html', {
        'produk': produk,
        'title': f'Hapus Produk - {produk.nama_produk}'
    })
