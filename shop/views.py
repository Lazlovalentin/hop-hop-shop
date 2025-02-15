from rest_framework.filters import OrderingFilter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from shop.models import Category, Product
from shop.serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductDetailSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend
from shop.filters import ProductFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view


@extend_schema(tags=["categories"])
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    @extend_schema(
        summary="Retrieve a list of categories",
        description="This endpoint returns a list of all categories. Supports pagination if configured.",
        responses={
            200: CategorySerializer(many=True),
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new category",
        description="This endpoint allows you to create a new category. You need to provide the required fields.",
        request=CategorySerializer,
        responses={
            201: CategorySerializer,
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a specific category",
        description="This endpoint returns the details of a specific category identified by its ID.",
        responses={
            200: CategorySerializer,
            404: "Category not found",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Update an existing category",
        description="This endpoint allows you to update an existing category identified by its ID. You only need to provide the fields you want to update.",
        request=CategorySerializer,
        responses={
            200: CategorySerializer,
            404: "Category not found",
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete a category",
        description="This endpoint allows you to delete a category identified by its ID.",
        responses={
            204: "Category deleted successfully",
            404: "Category not found",
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="category",
                description="Specify the category slug to filter the products.",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="name",
                description="Search by product name",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="ordering",
                description="Sort by fields: 'views' (popular product ), 'price'. Use '-' for short order.",
                required=False,
                type=str,
            ),
        ],
    ),
)
@extend_schema(tags=["products"])
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ProductFilter
    ordering_fields = ["views", "price"]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductSerializer

    @extend_schema(
        summary="Retrieve a list of products",
        description="This endpoint returns a list of products. You can filter by category slug and product name, and sort by fields such as 'views' or 'price'.",
        parameters=[
            OpenApiParameter(
                name="category",
                description="Specify the category slug to filter the products.",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="name",
                description="Search by product name.",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="ordering",
                description="Sort by fields: 'views' (popular product), 'price'. Use '-' for descending order.",
                required=False,
                type=str,
            ),
        ],
        responses={
            200: ProductSerializer(many=True),
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new product",
        description="This endpoint allows you to create a new product. You need to provide the required fields.",
        request=ProductSerializer,
        responses={
            201: ProductSerializer,
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a specific product",
        description="This endpoint returns the details of a specific product identified by its ID. It also increments the view count of the product.",
        responses={
            200: ProductDetailSerializer,
            404: "Product not found",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        summary="Update an existing product",
        description="This endpoint allows you to update an existing product identified by its ID. You only need to provide the fields you want to update.",
        request=ProductSerializer,
        responses={
            200: ProductDetailSerializer,
            404: "Product not found",
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete a product",
        description="This endpoint allows you to delete a product identified by its ID.",
        responses={
            204: "Product deleted successfully",
            404: "Product not found",
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve popular products",
        description="This endpoint returns the top 30 most viewed products.",
        responses={
            200: ProductSerializer(many=True),
        },
    )
    @action(detail=False, methods=["get"])
    def popular(self, request):
        popular_products = self.queryset.order_by("-views")[:30]
        serializer = self.get_serializer(popular_products, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Retrieve latest arrival products",
        description="This endpoint returns the latest 30 products based on their creation date.",
        responses={
            200: ProductSerializer(many=True),
        },
    )
    @action(detail=False, methods=["get"])
    def latest_arrival(self, request):
        latest_arrival_products = self.queryset.order_by("-pk")[:30]
        serializer = self.get_serializer(latest_arrival_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
