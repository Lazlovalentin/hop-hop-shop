import stripe
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from cart.services import CartSessionService
from checkout.models import Order, OrderItem
from shop.models import Product
from utils.custom_exceptions import (
    CartEmptyException,
    StripeCardError,
    StripeRateLimitError,
    StripeInvalidRequestError,
    StripeAuthenticationError,
    StripeAPIConnectionError,
    StripeGeneralError,
)

stripe.api_key = settings.STRIPE_SECRET_KEY


class OrderData:
    def __init__(self, order=None, card_information=None, total_price=0):
        self.order = order
        self.card_information = card_information
        self.total_price = total_price


class OrderService:
    def __init__(self, request):
        self.request = request
        self.cart_service = CartSessionService(request)

    def create_order(self, validated_data: dict):
        if not self._is_cart_not_empty():
            raise CartEmptyException
        card_information = validated_data.pop("card_information", None)
        order = self._create_order_instance(validated_data)
        self._create_order_items(order)

        total_price = self.cart_service.get_total_price()
        return OrderData(order, card_information, total_price)

    def _is_cart_not_empty(self) -> None:
        return self.cart_service.get_total_price() > 0

    def _create_order_instance(self, validated_data: dict) -> Order:
        return Order.objects.create(**validated_data)

    def _create_order_items(self, order: Order) -> None:
        items_data = self._get_cart_items()
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

    def _get_cart_items(self):
        return [
            {
                "product": Product.objects.get(id=item["product"]["id"]),
                "quantity": item["quantity"],
                "price": item["price"],
            }
            for item in self.cart_service
        ]

    def clear_cart(self):
        self.cart_service.clear()


class PaymentService:
    @staticmethod
    def stripe_card_payment(
        card_information: dict, total_price: float
    ) -> Response | Exception:
        payment_method_data = {
            "type": "card",
            "card": {
                "number": card_information["card_number"],
                "exp_month": card_information["expiry_month"],
                "exp_year": card_information["expiry_year"],
                "cvc": card_information["cvc"],
            },
        }
        try:
            stripe.PaymentIntent.create(
                amount=int(total_price * 100),
                currency="usd",
                payment_method_data=payment_method_data,
                confirm=True,
                return_url="http://127.0.0.1:8000/api/doc/",
            )
            return Response(status=status.HTTP_200_OK)
        except stripe.error.CardError as e:
            raise StripeCardError(detail=str(e))

        except stripe.error.RateLimitError as e:
            raise StripeRateLimitError(detail=str(e))

        except stripe.error.InvalidRequestError as e:
            raise StripeInvalidRequestError(detail=str(e))

        except stripe.error.AuthenticationError as e:
            raise StripeAuthenticationError(detail=str(e))

        except stripe.error.APIConnectionError as e:
            raise StripeAPIConnectionError(detail=str(e))

        except stripe.error.StripeError as e:
            raise StripeGeneralError(detail=str(e))
