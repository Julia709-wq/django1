from django.shortcuts import render
from django.views.generic import ListView, DetailView
from . models import Product


def contacts(request):
    return render(request, 'catalog/contacts.html')


def home(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'catalog/product_list.html', context=context)

class ProductsListView(ListView):
    model = Product

class ProductDetailView(DetailView):
    model = Product

# def product_detail(request, product_id):
#     product = Product.objects.get(id=product_id)
#     context = {
#         'product': product
#     }
#     return render(request, 'catalog/product_detail.html', context=context)

# def products_list(request):
#     products = Product.objects.all()
#     context = {'products': products}
#     return render(request, 'home.html', context=context)

