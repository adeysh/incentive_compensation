from decimal import Decimal, ROUND_HALF_UP


def calculate_percentage(base_amount, rate):
    """
    Calculate commission using a percentage rate.

    Example:
        base_amount = 70000
        rate = 5

        result = 3500
    """

    base = Decimal(str(base_amount))
    percentage = Decimal(str(rate))

    commission = base * percentage / Decimal("100")

    return commission.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


def calculate_fixed_amount(fixed_amount):
    """
    Return a fixed commission amount.
    """
    amount = Decimal(str(fixed_amount))

    return amount.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


def calculate_tiered(base_amount, tiers):
    """
    Calculate progressive tiered commission.

    Each tier should contain:
        from_amount
        to_amount
        rate

    Example:
        [
            {"from_amount": 0, "to_amount": 50000, "rate": 2},
            {"from_amount": 50000, "to_amount": 100000, "rate": 5},
            {"from_amount": 100000, "to_amount": None, "rate": 8},
        ]
    """

    base = Decimal(str(base_amount))
    total_commission = Decimal("0.00")

    for tier in tiers:
        from_amount = Decimal(str(tier["from_amount"]))
        to_amount = tier.get("to_amount")
        rate = Decimal(str(tier["rate"]))

        if to_amount is not None:
            to_amount = Decimal(str(to_amount))

        if base <= from_amount:
            continue

        tier_end = to_amount if to_amount is not None else base

        applicable_amount = min(base, tier_end) - from_amount

        if applicable_amount <= 0:
            continue

        commission = applicable_amount * rate / Decimal("100")
        total_commission += commission

        if to_amount is None or base <= to_amount:
            break

    return total_commission.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


def calculate_allocated_amount(base_amount, allocated_percentage):
    """
    Calculate the portion of a transaction assigned to a Sales Person.
    """

    base = Decimal(str(base_amount))
    percentage = Decimal(str(allocated_percentage))

    allocated_amount = base * percentage / Decimal("100")

    return allocated_amount.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )
