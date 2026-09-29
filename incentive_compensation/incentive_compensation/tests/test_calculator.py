from decimal import Decimal
import unittest

from incentive_compensation.incentive_compensation.commission_engine.calculator import (
    calculate_percentage,
    calculate_fixed_amount,
    calculate_tiered,
    calculate_allocated_amount,
)


class TestCalculator(unittest.TestCase):

    def test_percentage_commission(self):
        result = calculate_percentage(1000, 10)

        self.assertEqual(result, Decimal("100"))

    def test_percentage_commission_decimal_rate(self):
        result = calculate_percentage(1000, 7.5)

        self.assertEqual(result, Decimal("75"))

    def test_percentage_commission_rounding(self):
        result = calculate_percentage(100, 2.555)

        self.assertEqual(result, Decimal("2.56"))

    def test_fixed_amount(self):
        result = calculate_fixed_amount(250)

        self.assertEqual(result, Decimal("250"))

    def test_fixed_amount_rounding(self):
        result = calculate_fixed_amount(100.555)

        self.assertEqual(result, Decimal("100.56"))

    def test_tiered_commission(self):
        tiers = [
            {
                "from_amount": 0,
                "to_amount": 1000,
                "rate": 5,
            },
            {
                "from_amount": 1000,
                "to_amount": 5000,
                "rate": 10,
            },
            {
                "from_amount": 5000,
                "to_amount": None,
                "rate": 15,
            },
        ]

        result = calculate_tiered(6000, tiers)

        self.assertEqual(result, Decimal("600"))

    def test_tiered_commission_first_tier_only(self):
        tiers = [
            {
                "from_amount": 0,
                "to_amount": 1000,
                "rate": 5,
            },
            {
                "from_amount": 1000,
                "to_amount": 5000,
                "rate": 10,
            },
        ]

        result = calculate_tiered(500, tiers)

        self.assertEqual(result, Decimal("25"))

    def test_tiered_commission_second_tier(self):
        tiers = [
            {
                "from_amount": 0,
                "to_amount": 1000,
                "rate": 5,
            },
            {
                "from_amount": 1000,
                "to_amount": 5000,
                "rate": 10,
            },
        ]

        result = calculate_tiered(3000, tiers)

        self.assertEqual(result, Decimal("250"))

    def test_allocated_amount(self):
        result = calculate_allocated_amount(1000, 50)

        self.assertEqual(result, Decimal("500"))

    def test_allocated_amount_full_allocation(self):
        result = calculate_allocated_amount(1000, 100)

        self.assertEqual(result, Decimal("1000"))

    def test_allocated_amount_partial_allocation(self):
        result = calculate_allocated_amount(1000, 25)

        self.assertEqual(result, Decimal("250"))
