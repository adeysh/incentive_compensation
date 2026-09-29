from .calculator import (
    calculate_fixed_amount,
    calculate_percentage,
    calculate_tiered,
)


def calculate_commission(rule, base_amount, tiers=None):
    """
    Calculate commission using the method defined by a Commission Rule.

    Returns a structured calculation result.
    """

    calculation_method = rule.get("calculation_method")

    result = {
        "commission_rule": rule.get("name"),
        "calculation_method": calculation_method,
        "base_amount": base_amount,
        "commission_amount": None,
    }

    if calculation_method == "Percentage":
        rate = rule.get("rate")

        commission = calculate_percentage(
            base_amount,
            rate,
        )

        result["rate"] = rate

    elif calculation_method == "Fixed Amount":
        fixed_amount = rule.get("fixed_amount")

        commission = calculate_fixed_amount(
            fixed_amount,
        )

        result["fixed_amount"] = fixed_amount

    elif calculation_method == "Tiered":
        if not tiers:
            raise ValueError("Tiered commission requires tiers.")

        commission = calculate_tiered(
            base_amount,
            tiers,
        )

    else:
        raise ValueError(f"Unsupported calculation method: {calculation_method}")

    result["commission_amount"] = commission

    return result
