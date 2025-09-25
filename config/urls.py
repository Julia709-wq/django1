from django.contrib import admin
from django.urls import path, include
from catalog import views
from catalog.views import ProductDetailView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('catalog.urls', namespace='catalog')),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
]
