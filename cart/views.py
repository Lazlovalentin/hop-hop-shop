from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Coupon
from cart.serializers import CouponSerializer
from shop.models import Product
from cart.services import CartService
from utils.custom_exceptions import (
    ProductNotExistException,
)


def cart_session_response(cart_service):
    cart_items = cart_service
    total_price = cart_service.get_total_price()
    total_items = cart_service.get_total_item()
    coupon_is_used = cart_service.coupon_is_used()

    return {
        "products": cart_items,
        "total_items": total_items,
        "subtotal_price": total_price,
        "total_price": total_price,
        "coupon_is_used": coupon_is_used,
    }


@extend_schema(summary="Retrieve cart details")
class CartDetailView(APIView):
    """
    Retrieve the details of the cart.
    """

    def get(self, request):
        cart = CartService(request)
        response_data = cart_session_response(cart)

        return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(summary="Add item to cart")
class CartAddItemView(APIView):
    """
    Add an item to the cart.
    """

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ProductNotExistException

        cart = CartService(request)
        cart.add(
            product=product,
            quantity=request.data.get("quantity", 1),
            update_quantity=request.data.get("update_quantity", False),
        )
        response_data = cart_session_response(cart)
        return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(summary="Remove item from cart")
class CartRemoveItemView(APIView):
    """
    Remove an item from the cart.
    """

    def delete(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ProductNotExistException

        cart = CartService(request)
        cart.remove(product)
        response_data = cart_session_response(cart)
        return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(summary="Subtract item quantity in cart")
class CartSubtractItemView(APIView):
    """
    Subtract the quantity of an item in the cart.
    """

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ProductNotExistException

        cart = CartService(request)
        cart.subtract_quantity(product)
        response_data = cart_session_response(cart)
        return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(tags=["coupon"], summary="Apply coupon")
class UseCouponView(APIView):
    """
    Apply a coupon to the cart.
    """

    serializer_class = CouponSerializer

    def post(self, request):
        code = request.data.get("code")
        try:
            coupon = Coupon.objects.get(code=code, active=True)
        except Coupon.DoesNotExist:
            raise ProductNotExistException

        cart = CartService(request)
        cart.add_coupon(coupon)
        response_data = cart_session_response(cart)
        return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(tags=["coupon"], summary="Cancel applied coupon")
class RemoveCouponView(APIView):
    """
    Remove an applied coupon from the cart.
    """

    def post(self, request):
        cart = CartService(request)
        cart.remove_coupon()
        return Response(cart, status=status.HTTP_200_OK)
