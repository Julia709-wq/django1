from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseForbidden

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from . models import Product, Category
from .forms import ProductForm
from .services import ProductService


def contacts(request):
    return render(request, 'catalog/contacts.html')


def home(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'catalog/product_list.html', context=context)

class ProductsListView(ListView):
    model = Product

    def get_queryset(self):  # низкоуровневое кэширование
        queryset = cache.get('products_queryset')
        if not queryset:
            queryset = super().get_queryset()
            cache.set('products_queryset', queryset, 60 * 15)
        return queryset

@method_decorator(cache_page(60 * 15), name='dispatch')
class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:home')

    def form_valid(self, form):
        product = form.save()
        user = self.request.user
        product.owner = user
        product.save()
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy('catalog:home')

    def get_form_class(self):
        user = self.request.user
        if user == self.object.owner:
            return ProductForm
        raise PermissionDenied('У Вас нет прав для редактирования продукта.')


class ProductDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:home')
    permission_required = 'catalog.delete_product'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.owner != self.request.user:
            raise PermissionDenied('У Вас нет прав для удаления продукта.')
        return obj


class UnpublishProductView(View):
    def post(self, request, pk):
        product = get_object_or_404(Product, id=pk)

        if not request.user.has_perm('catalog.can_unpublish_product'):
            return HttpResponseForbidden("У Вас нет прав для отмены публикации продукта.")

        product.is_published = False
        product.save()
        return redirect('catalog:home')


def products_by_category_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = ProductService.get_by_category(category_id)

    return render(request, 'catalog/category_products.html', {
        'category': category,
        'products': products
    })
