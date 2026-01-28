from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q

from products.models import Produk, Status
from products.forms import ProdukForm


def produk_list(request):
    """
    Display list of products with optional status filter.
    """
    # Get filter parameter from URL (?show=all or default to bisa_dijual)
    show_filter = request.GET.get('show', 'bisa_dijual')
    
    # Get all products with related data
    produk_list = Produk.objects.all().select_related('kategori', 'status')
    
    # Apply filter if not showing all
    if show_filter != 'all':
        try:
            bisa_dijual_status = Status.objects.get(nama_status__iexact='bisa dijual')
            produk_list = produk_list.filter(status=bisa_dijual_status)
            title = 'Daftar Produk - Bisa Dijual'
        except Status.DoesNotExist:
            messages.warning(request, 'Status "bisa dijual" tidak ditemukan. Menampilkan semua produk.')
            title = 'Daftar Produk - Semua'
    else:
        title = 'Daftar Produk - Semua'
    
    context = {
        'produk_list': produk_list,
        'title': title,
        'show_filter': show_filter,
    }
    return render(request, 'products/produk_list.html', context)


def produk_detail(request, pk):
    """
    Display detail of a single product.
    """
    produk = get_object_or_404(Produk, pk=pk)
    context = {
        'produk': produk,
        'title': f'Detail Produk - {produk.nama_produk}'
    }
    return render(request, 'products/produk_detail.html', context)


def produk_create(request):
    """
    Create a new product.
    """
    if request.method == 'POST':
        form = ProdukForm(request.POST)
        if form.is_valid():
            produk = form.save()
            messages.success(request, f'Produk "{produk.nama_produk}" berhasil ditambahkan!')
            return redirect('produk_list')
    else:
        form = ProdukForm()
    
    context = {
        'form': form,
        'title': 'Tambah Produk',
        'action': 'Tambah'
    }
    return render(request, 'products/produk_form.html', context)


def produk_update(request, pk):
    """
    Update an existing product.
    """
    produk = get_object_or_404(Produk, pk=pk)
    
    if request.method == 'POST':
        form = ProdukForm(request.POST, instance=produk)
        if form.is_valid():
            produk = form.save()
            messages.success(request, f'Produk "{produk.nama_produk}" berhasil diperbarui!')
            # Redirect to detail page to show the updated product
            return redirect('produk_detail', pk=produk.pk)
    else:
        form = ProdukForm(instance=produk)
    
    context = {
        'form': form,
        'title': f'Edit Produk - {produk.nama_produk}',
        'action': 'Perbarui',
        'produk': produk
    }
    return render(request, 'products/produk_form.html', context)


def produk_delete(request, pk):
    """
    Delete a product.
    """
    produk = get_object_or_404(Produk, pk=pk)
    
    if request.method == 'POST':
        nama_produk = produk.nama_produk
        produk.delete()
        messages.success(request, f'Produk "{nama_produk}" berhasil dihapus!')
        return redirect('produk_list')
    
    context = {
        'produk': produk,
        'title': f'Hapus Produk - {produk.nama_produk}'
    }
    return render(request, 'products/produk_confirm_delete.html', context)
