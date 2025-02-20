# from unittest.mock import Mock
# from django.test import TestCase
# from django.urls import reverse
# from django.conf import settings
# from shop.models import Product, Category
# from rest_framework import status
# from rest_framework.test import APIClient
# from .services import WishlistService
#
#
# class WishlistServiceTests(TestCase):
#     def setUp(self):
#         self.category = Category.objects.create(name="Test Category")
#         self.product = Product.objects.create(
#             name="Test Product",
#             category=self.category,
#             slug="test-product",
#             price=100.00,
#             SKU=1001,
#             description="Test description",
#         )
#         self.client = APIClient()
#         self.session = self.client.session
#
#     def tearDown(self):
#         self.session.clear()
#         self.session.save()
#
#     def test_add_product_to_wishlist(self):
#         service = WishlistService(self.client)
#         service.add_product(5)
#
#         url = reverse("add_to_wishlists", args=[5])
#         response = self.client.post(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#         service_wishlist = service.session.get(settings.WISHLIST_SESSION_ID, [])
#         self.assertIn(5, service_wishlist)
#
#     def test_remove_product_from_wishlist(self):
#         self.session[settings.WISHLIST_SESSION_ID] = [self.product.id]
#         self.session.save()
#
#         url = reverse("remove_from_wishlists", args=[self.product.id])
#         response = self.client.post(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#         service = WishlistService(self.client)
#         service_wishlist = service.session.get(settings.WISHLIST_SESSION_ID, [])
#         self.assertNotIn(self.product.id, service_wishlist)
#
#     def test_view_products_in_wishlist(self):
#         self.session[settings.WISHLIST_SESSION_ID] = [self.product.id]
#         self.session.save()
#
#         url = reverse("view_wishlists")
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data["products"]), 1)
#         self.assertEqual(response.data["products"][0]["id"], self.product.id)
#
#     def test_get_products(self):
#         mock_request = Mock()
#         service = WishlistService(mock_request)
#         service.wishlist = [1, 2, 3]
#         products = service.get_products()
#         self.assertEqual(len(products), 3)
#
#     def test_iterator(self):
#         mock_request = Mock()
#         service = WishlistService(mock_request)
#         service.wishlist = [1, 2, 3]
#         iterator = iter(service)
#         for serialized_product in iterator:
#             self.assertIsInstance(serialized_product, dict)
