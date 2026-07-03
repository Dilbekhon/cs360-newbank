from decimal import Decimal

from django.test import TestCase

from .services import convert_currency


class CurrencyConversionTest(TestCase):

    def test_usd_to_uzs_with_bank_fee(self):
        result = convert_currency(
            amount=Decimal("100"),
            from_currency="USD",
            to_currency="UZS"
        )

        self.assertEqual(result, Decimal("1234800.00"))

    def test_uzs_to_usd_with_bank_fee(self):
        result = convert_currency(
            amount=Decimal("1260000"),
            from_currency="UZS",
            to_currency="USD"
        )

        self.assertEqual(result, Decimal("98.00"))

    def test_unsupported_currency_pair_raises_error(self):
        with self.assertRaises(ValueError):
            convert_currency(
                amount=Decimal("100"),
                from_currency="USD",
                to_currency="EUR"
            )