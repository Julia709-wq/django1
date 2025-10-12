from django import forms
from django.core.exceptions import ValidationError

from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'description', 'category', 'price', 'image']

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)

        self.fields['product_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите название продукта'
        })
        self.fields['description'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите описание продукта'
        })
        self.fields['category'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['price'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите цену продукта'
        })
        self.fields['image'].widget.attrs.update({
            'class': 'form-control'
        })

    def clean_product_name(self):
        product_name = self.cleaned_data.get('product_name')
        if not product_name:
            return product_name

        forbidden_words = ['казино', 'криптовалюта', 'крипта', 'биржа', 'дешево', 'бесплатно', 'обман', 'полиция', 'радар']
        product_name_lower = product_name.lower()

        for word in forbidden_words:
            if word in product_name_lower:
                raise ValidationError('Название продукта содержит запрещенное слово')
        return product_name


    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description:
            return description

        forbidden_words = ['казино', 'криптовалюта', 'крипта', 'биржа', 'дешево', 'бесплатно', 'обман', 'полиция', 'радар']
        description_lower = description.lower()

        for word in forbidden_words:
            if word in description_lower:
                raise ValidationError('Описание содержит запрещенное слово')
        return description


    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price < 0:
            raise ValidationError('Цена не может быть отрицательной')
        return price


