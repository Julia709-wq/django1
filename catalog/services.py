from .models import Product


class ProductService:
    @staticmethod
    def get_by_category(category_id):
        return Product.objects.filter(category_id=category_id, is_published=True)
