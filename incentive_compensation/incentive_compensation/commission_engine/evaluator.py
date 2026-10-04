import frappe

from .calculator import calculate_allocated_amount
from .engine import calculate_commission
from .resolver import (
    get_applicable_plan,
    get_matching_rules,
    get_rule_tiers,
    get_commission_payee,
)
from .transaction_builder import build_transactions_from_sales_invoice


def evaluate_transaction(transaction):
    """
    Evaluate a transaction and return commission calculations.

    Expected transaction fields:
        company
        transaction_date
        item
        item_group
        sales_person
        customer
        customer_group
        territory
        base_amount
    """

    plan = get_applicable_plan(
        transaction["company"],
        transaction["transaction_date"],
    )

    if not plan:
        return []

    matching_rules = get_matching_rules(
        transaction,
        plan,
    )

    if not matching_rules:
        return []

    allocated_base_amount = calculate_allocated_amount(
        transaction["base_amount"],
        transaction.get("allocated_percentage", 100),
    )

    rule = matching_rules[0]

    tiers = None

    if rule.calculation_method == "Tiered":
        tiers = get_rule_tiers(rule.name)

    result = calculate_commission(
        rule,
        allocated_base_amount,
        tiers,
    )

    commission_payee = get_commission_payee(transaction.get("sales_person"))

    if not commission_payee:
        frappe.throw(
            f"No active Commission Payee found for Sales Person "
            f'"{transaction.get("sales_person")}".',
            title="Commission Payee Missing",
            exc=frappe.ValidationError,
        )

    result["commission_plan"] = rule.commission_plan
    result["commission_payee"] = commission_payee
    result["sales_person"] = transaction.get("sales_person")
    result["allocated_percentage"] = transaction.get(
        "allocated_percentage",
        100,
    )

    return [result]


def evaluate_sales_invoice(invoice):
    transactions = build_transactions_from_sales_invoice(invoice)

    evaluations = []

    for transaction in transactions:
        results = evaluate_transaction(transaction)

        for result in results:
            evaluations.append(
                {
                    "transaction": transaction,
                    "result": result,
                }
            )

    return evaluations
