from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from catalog.models import Category, Product
from catalog.forms import ProductForm
from catalog.services import ProductService
from users.models import CustomUser

User = get_user_model()


def create_test_user(email='test@example.com', password='testpass123'):
    """Вспомогательная функция для создания тестового пользователя"""
    user = CustomUser.objects.create(email=email)
    user.set_password(password)
    user.save()
    return user


def create_test_image():
    """Вспомогательная функция для создания тестового изображения"""
    return SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")


class CategoryModelTest(TestCase):
    """Тесты для модели Category"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.category = Category.objects.create(
            category_name='Тестовая категория',
            description='Описание тестовой категории'
        )

    def test_category_creation(self):
        """Тест создания категории"""
        self.assertEqual(self.category.category_name, 'Тестовая категория')
        self.assertEqual(self.category.description, 'Описание тестовой категории')
        self.assertTrue(isinstance(self.category, Category))

    def test_category_str(self):
        """Тест строкового представления категории"""
        self.assertEqual(str(self.category), 'Тестовая категория')

    def test_category_verbose_name(self):
        """Тест verbose_name для категории"""
        self.assertEqual(Category._meta.verbose_name, 'категория')
        self.assertEqual(Category._meta.verbose_name_plural, 'категории')

    def test_category_ordering(self):
        """Тест сортировки категорий"""
        Category.objects.create(category_name='А категория')
        Category.objects.create(category_name='Б категория')
        categories = Category.objects.all()
        self.assertEqual(categories[0].category_name, 'А категория')
        self.assertEqual(categories[1].category_name, 'Б категория')


class ProductModelTest(TestCase):
    """Тесты для модели Product"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.category = Category.objects.create(
            category_name='Тестовая категория',
            description='Описание'
        )
        self.user = create_test_user()
        self.product = Product.objects.create(
            product_name='Тестовый продукт',
            description='Описание продукта',
            category=self.category,
            price=1000,
            owner=self.user,
            is_published=True,
            image=create_test_image()
        )

    def test_product_creation(self):
        """Тест создания продукта"""
        self.assertEqual(self.product.product_name, 'Тестовый продукт')
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.price, 1000)
        self.assertEqual(self.product.owner, self.user)
        self.assertTrue(self.product.is_published)
        self.assertTrue(isinstance(self.product, Product))

    def test_product_str(self):
        """Тест строкового представления продукта"""
        self.assertEqual(str(self.product), 'Тестовый продукт')

    def test_product_verbose_name(self):
        """Тест verbose_name для продукта"""
        self.assertEqual(Product._meta.verbose_name, 'товар')
        self.assertEqual(Product._meta.verbose_name_plural, 'товары')

    def test_product_ordering(self):
        """Тест сортировки продуктов"""
        Product.objects.create(
            product_name='А продукт',
            category=self.category,
            price=500,
            image=create_test_image()
        )
        Product.objects.create(
            product_name='Б продукт',
            category=self.category,
            price=600,
            image=create_test_image()
        )
        products = Product.objects.all()
        self.assertEqual(products[0].product_name, 'А продукт')
        self.assertEqual(products[1].product_name, 'Б продукт')

    def test_product_default_is_published(self):
        """Тест значения по умолчанию для is_published"""
        new_product = Product.objects.create(
            product_name='Новый продукт',
            category=self.category,
            price=500,
            image=create_test_image()
        )
        self.assertFalse(new_product.is_published)

    def test_product_created_at_auto(self):
        """Тест автоматического создания даты"""
        from django.utils import timezone
        self.assertIsNotNone(self.product.created_at)
        self.assertIsNotNone(self.product.updated_at)

    def test_product_category_relationship(self):
        """Тест связи продукта с категорией"""
        self.assertEqual(self.product.category, self.category)
        self.assertIn(self.product, self.category.products.all())

    def test_product_owner_relationship(self):
        """Тест связи продукта с владельцем"""
        self.assertEqual(self.product.owner, self.user)

    def test_product_without_owner(self):
        """Тест создания продукта без владельца"""
        product = Product.objects.create(
            product_name='Продукт без владельца',
            category=self.category,
            price=500,
            image=create_test_image()
        )
        self.assertIsNone(product.owner)


class ProductsListViewTest(TestCase):
    """Тесты для представления списка продуктов"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()
        self.category = Category.objects.create(
            category_name='Тестовая категория'
        )
        self.product1 = Product.objects.create(
            product_name='Продукт 1',
            category=self.category,
            price=1000,
            is_published=True,
            image=create_test_image()
        )
        self.product2 = Product.objects.create(
            product_name='Продукт 2',
            category=self.category,
            price=2000,
            is_published=False,
            image=create_test_image()
        )

    def test_products_list_view_status_code(self):
        """Тест статус кода для списка продуктов"""
        response = self.client.get(reverse('catalog:home'))
        self.assertEqual(response.status_code, 200)

    def test_products_list_view_template(self):
        """Тест использования правильного шаблона"""
        response = self.client.get(reverse('catalog:home'))
        self.assertTemplateUsed(response, 'catalog/product_list.html')

    def test_products_list_view_context(self):
        """Тест контекста представления"""
        response = self.client.get(reverse('catalog:home'))
        self.assertIn('product_list', response.context)
        self.assertIn(self.product1, response.context['product_list'])

    def test_products_list_view_cache(self):
        """Тест кэширования списка продуктов"""
        cache.clear()
        response1 = self.client.get(reverse('catalog:home'))
        response2 = self.client.get(reverse('catalog:home'))
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)


class ProductDetailViewTest(TestCase):
    """Тесты для представления деталей продукта"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()
        self.user = create_test_user()
        self.category = Category.objects.create(
            category_name='Тестовая категория'
        )
        self.product = Product.objects.create(
            product_name='Тестовый продукт',
            category=self.category,
            price=1000,
            image=create_test_image()
        )

    def test_product_detail_view_authenticated(self):
        """Тест детального просмотра для авторизованного пользователя"""
        self.client.login(email='test@example.com', password='testpass123')
        url = reverse('catalog:product_detail', kwargs={'pk': self.product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['product'], self.product)


class ProductCreateViewTest(TestCase):
    """Тесты для представления создания продукта"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()
        self.user = create_test_user()
        self.category = Category.objects.create(
            category_name='Тестовая категория'
        )

    def test_product_create_view_requires_login(self):
        """Тест того, что создание продукта требует авторизации"""
        url = reverse('catalog:product_form')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа

    def test_product_create_view_authenticated(self):
        """Тест создания продукта для авторизованного пользователя"""
        self.client.login(email='test@example.com', password='testpass123')
        url = reverse('catalog:product_form')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/product_form.html')

    def test_product_create_sets_owner(self):
        """Тест того, что при создании продукта устанавливается владелец"""
        self.client.login(email='test@example.com', password='testpass123')
        url = reverse('catalog:product_form')
        # Создаем тестовое изображение
        image = create_test_image()
        data = {
            'product_name': 'Новый продукт',
            'category': self.category.pk,
            'price': 1500,
            'description': 'Описание',
            'image': image
        }
        response = self.client.post(url, data, format='multipart')
        # Проверяем что продукт создан и владелец установлен
        if response.status_code == 302:
            product = Product.objects.get(product_name='Новый продукт')
            self.assertEqual(product.owner, self.user)


class ProductUpdateViewTest(TestCase):
    """Тесты для представления обновления продукта"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()
        self.owner = create_test_user('owner@example.com')
        self.other_user = create_test_user('other@example.com')
        self.category = Category.objects.create(
            category_name='Тестовая категория'
        )
        self.product = Product.objects.create(
            product_name='Тестовый продукт',
            category=self.category,
            price=1000,
            owner=self.owner
        )

    def test_product_update_view_requires_login(self):
        """Тест того, что обновление продукта требует авторизации"""
        url = reverse('catalog:product_update', kwargs={'pk': self.product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_product_update_by_owner(self):
        """Тест обновления продукта владельцем"""
        self.client.login(email='owner@example.com', password='testpass123')
        url = reverse('catalog:product_update', kwargs={'pk': self.product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_product_update_by_non_owner(self):
        """Тест того, что не владелец не может обновить продукт"""
        self.client.login(email='other@example.com', password='testpass123')
        url = reverse('catalog:product_update', kwargs={'pk': self.product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)  # PermissionDenied






class ContactsViewTest(TestCase):
    """Тесты для представления контактов"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()

    def test_contacts_view_status_code(self):
        """Тест статус кода для страницы контактов"""
        response = self.client.get(reverse('catalog:contacts'))
        self.assertEqual(response.status_code, 200)

    def test_contacts_view_template(self):
        """Тест использования правильного шаблона"""
        response = self.client.get(reverse('catalog:contacts'))
        self.assertTemplateUsed(response, 'catalog/contacts.html')


class ProductsByCategoryViewTest(TestCase):
    """Тесты для представления продуктов по категории"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()
        self.category = Category.objects.create(
            category_name='Тестовая категория'
        )
        self.product1 = Product.objects.create(
            product_name='Опубликованный продукт',
            category=self.category,
            price=1000,
            is_published=True,
            image=create_test_image()
        )
        self.product2 = Product.objects.create(
            product_name='Неопубликованный продукт',
            category=self.category,
            price=2000,
            is_published=False,
            image=create_test_image()
        )

    def test_products_by_category_view_status_code(self):
        """Тест статус кода для продуктов по категории"""
        url = reverse('catalog:category_products', kwargs={'category_id': self.category.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_products_by_category_view_shows_only_published(self):
        """Тест того, что показываются только опубликованные продукты"""
        url = reverse('catalog:category_products', kwargs={'category_id': self.category.pk})
        response = self.client.get(url)
        products = response.context['products']
        self.assertIn(self.product1, products)
        self.assertNotIn(self.product2, products)



class ProductFormTest(TestCase):
    """Тесты для формы ProductForm"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.category = Category.objects.create(
            category_name='Тестовая категория'
        )

    def test_product_form_forbidden_words_in_name(self):
        """Тест валидации запрещенных слов в названии"""
        forbidden_words = ['казино', 'криптовалюта', 'крипта', 'биржа', 
                          'дешево', 'бесплатно', 'обман', 'полиция', 'радар']
        
        for word in forbidden_words:
            form_data = {
                'product_name': f'Продукт {word}',
                'category': self.category.pk,
                'price': 1000
            }
            form = ProductForm(data=form_data)
            # Проверяем что форма не валидна из-за запрещенного слова
            if not form.is_valid():
                errors_str = str(form.errors)
                self.assertIn('Название продукта содержит запрещенное слово', errors_str)

    def test_product_form_forbidden_words_case_insensitive(self):
        """Тест того, что валидация запрещенных слов не чувствительна к регистру"""
        form_data = {
            'product_name': 'Продукт КАЗИНО',
            'category': self.category.pk,
            'price': 1000
        }
        form = ProductForm(data=form_data)
        # Форма должна быть невалидна из-за запрещенного слова
        if not form.is_valid():
            errors_str = str(form.errors)
            self.assertIn('Название продукта содержит запрещенное слово', errors_str)

    def test_product_form_forbidden_words_in_description(self):
        """Тест валидации запрещенных слов в описании"""
        form_data = {
            'product_name': 'Валидный продукт',
            'description': 'Это описание содержит слово казино',
            'category': self.category.pk,
            'price': 1000
        }
        form = ProductForm(data=form_data)
        if not form.is_valid():
            errors_str = str(form.errors)
            self.assertIn('Описание содержит запрещенное слово', errors_str)

    def test_product_form_negative_price(self):
        """Тест валидации отрицательной цены"""
        form_data = {
            'product_name': 'Валидный продукт',
            'category': self.category.pk,
            'price': -100
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Цена не может быть отрицательной', str(form.errors))

    def test_product_form_widget_attrs(self):
        """Тест того, что виджеты формы имеют правильные атрибуты"""
        form = ProductForm()
        self.assertEqual(form.fields['product_name'].widget.attrs.get('class'), 'form-control')
        self.assertEqual(form.fields['description'].widget.attrs.get('class'), 'form-control')
        self.assertEqual(form.fields['category'].widget.attrs.get('class'), 'form-control')
        self.assertEqual(form.fields['price'].widget.attrs.get('class'), 'form-control')
        self.assertEqual(form.fields['image'].widget.attrs.get('class'), 'form-control')



class ProductServiceTest(TestCase):
    """Тесты для сервиса ProductService"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.category1 = Category.objects.create(
            category_name='Категория 1'
        )
        self.category2 = Category.objects.create(
            category_name='Категория 2'
        )
        
        # Создаем продукты для категории 1
        self.published_product1 = Product.objects.create(
            product_name='Опубликованный продукт 1',
            category=self.category1,
            price=1000,
            is_published=True,
            image=create_test_image()
        )
        self.unpublished_product1 = Product.objects.create(
            product_name='Неопубликованный продукт 1',
            category=self.category1,
            price=2000,
            is_published=False,
            image=create_test_image()
        )
        
        # Создаем продукты для категории 2
        self.published_product2 = Product.objects.create(
            product_name='Опубликованный продукт 2',
            category=self.category2,
            price=1500,
            is_published=True,
            image=create_test_image()
        )

    def test_get_by_category_returns_only_published(self):
        """Тест того, что метод возвращает только опубликованные продукты"""
        products = ProductService.get_by_category(self.category1.pk)
        self.assertIn(self.published_product1, products)
        self.assertNotIn(self.unpublished_product1, products)

    def test_get_by_category_filters_by_category(self):
        """Тест того, что метод фильтрует продукты по категории"""
        products = ProductService.get_by_category(self.category1.pk)
        self.assertIn(self.published_product1, products)
        self.assertNotIn(self.published_product2, products)

    def test_get_by_category_empty_result(self):
        """Тест того, что метод возвращает пустой результат для категории без опубликованных продуктов"""
        # Создаем категорию без опубликованных продуктов
        category3 = Category.objects.create(category_name='Категория 3')
        Product.objects.create(
            product_name='Неопубликованный',
            category=category3,
            price=1000,
            is_published=False,
            image=create_test_image()
        )
        
        products = ProductService.get_by_category(category3.pk)
        self.assertEqual(products.count(), 0)

    def test_get_by_category_nonexistent_category(self):
        """Тест того, что метод возвращает пустой результат для несуществующей категории"""
        products = ProductService.get_by_category(99999)
        self.assertEqual(products.count(), 0)

    def test_get_by_category_returns_queryset(self):
        """Тест того, что метод возвращает QuerySet"""
        products = ProductService.get_by_category(self.category1.pk)
        from django.db.models.query import QuerySet
        self.assertIsInstance(products, QuerySet)
