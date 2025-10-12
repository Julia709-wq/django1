from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseForbidden

from . models import Product
from .forms import ProductForm


def contacts(request):
    return render(request, 'catalog/contacts.html')


def home(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'catalog/product_list.html', context=context)

class ProductsListView(ListView):
    model = Product

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


class UnpublishProductView(View):
    def post(self, request, pk):
        product = get_object_or_404(Product, id=pk)

        if not request.user.has_perm('catalog.can_unpublish_product'):
            return HttpResponseForbidden("У Вас нет прав для отмены публикации продукта.")

        product.is_published = False
        product.save()
        return redirect('catalog:home')
