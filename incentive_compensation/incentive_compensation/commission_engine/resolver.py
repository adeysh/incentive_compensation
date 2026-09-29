import frappe
from frappe.utils import getdate


def get_active_plans(company, transaction_date):
    """
    Return Commission Plans that are active for the given company
    and transaction date.
    """

    transaction_date = getdate(transaction_date)

    filters = {
        "company": company,
        "status": "Active",
        "valid_from": ["<=", transaction_date],
    }

    plans = frappe.get_all(
        "Commission Plan",
        filters=filters,
        fields=[
            "name",
            "plan_name",
            "company",
            "currency",
            "valid_from",
            "valid_to",
            "status",
        ],
        order_by="valid_from desc",
    )

    valid_plans = []

    for plan in plans:
        if plan.valid_to and plan.valid_to < transaction_date:
            continue

        valid_plans.append(plan)

    return valid_plans


def get_applicable_plan(company, transaction_date):
    """
    Return the Commission Plan that is the most recent
    """
    active_plans = get_active_plans(
        company,
        transaction_date,
    )

    if not active_plans:
        return None

    return active_plans[0]


def get_matching_rules(transaction, plan):
    """
    Find enabled Commission Rules that match a transaction
    and belong to one of the selected active Commission Plan.
    """

    if not plan:
        return []

    rules = frappe.get_all(
        "Commission Rule",
        filters={
            "enabled": 1,
            "commission_plan": plan.name,
        },
        fields=[
            "name",
            "rule_name",
            "commission_plan",
            "priority",
            "based_on",
            "item",
            "item_group",
            "sales_person",
            "customer",
            "customer_group",
            "territory",
            "calculation_method",
            "fixed_amount",
            "rate",
        ],
    )

    matching_rules = []

    for rule in rules:
        if _rule_matches(rule, transaction):
            matching_rules.append(rule)

    matching_rules.sort(key=lambda rule: rule.priority)

    return matching_rules


def _rule_matches(rule, transaction):
    """
    Check whether a Commission Rule matches a transaction.
    """

    based_on = rule.based_on

    if based_on == "Item":
        return rule.item == transaction.get("item")

    if based_on == "Item Group":
        return rule.item_group == transaction.get("item_group")

    if based_on == "Sales Person":
        return rule.sales_person == transaction.get("sales_person")

    if based_on == "Customer":
        return rule.customer == transaction.get("customer")

    if based_on == "Customer Group":
        return rule.customer_group == transaction.get("customer_group")

    if based_on == "Territory":
        return rule.territory == transaction.get("territory")

    return False


def get_rule_tiers(rule_name):
    """
    Return the tiers configured for a Commission Rule.
    """

    rule = frappe.get_doc("Commission Rule", rule_name)

    return [
        {
            "from_amount": tier.from_amount,
            "to_amount": tier.to_amount or None,
            "rate": tier.rate,
            "description": tier.description,
        }
        for tier in rule.tiers
    ]


def get_commission_payee(sales_person):
    if not sales_person:
        return None

    payees = frappe.get_all(
        "Commission Payee",
        filters={
            "sales_person": sales_person,
            "enabled": 1,
        },
        fields=["name"],
        limit=1,
    )

    if not payees:
        return None

    return payees[0].name
