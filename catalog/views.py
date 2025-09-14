from django.shortcuts import render
from . models import Product


# def home(request):
#     return render(request, 'home.html')


def contacts(request):
    return render(request, 'contacts.html')


def home(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'home.html', context=context)


def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    context = {
        'product': product
    }
    return render(request, 'product_detail.html', context=context)


def products_list(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'home.html', context=context)
