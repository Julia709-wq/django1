from django.db import models
from users.models import CustomUser


class Category(models.Model):
    category_name = models.CharField(max_length=200, verbose_name='Наименование категории')
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'
        ordering = ['category_name']


class Product(models.Model):
    product_name = models.CharField(max_length=200, verbose_name='Название продукта')
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='photos/', verbose_name='Изображение', )
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, related_name='products')
    price = models.IntegerField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now_add=True)

    owner = models.ForeignKey(CustomUser, verbose_name='Владелец', blank=True, null=True, on_delete=models.SET_NULL)
    is_published = models.BooleanField(default=False, verbose_name='Статус публикации')

    def __str__(self):
        return self.product_name

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'
        ordering = ['product_name']
        permissions = [
            ('can_unpublish_product', 'Can unpublish product'),
        ]
