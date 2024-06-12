import django_filters
from shop.models import Product


class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(
        field_name="category__slug", lookup_expr="iexact"
    )

    class Meta:
        model = Product
        fields = ["category"]
