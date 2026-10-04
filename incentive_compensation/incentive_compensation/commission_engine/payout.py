import frappe
from .permissions import require_role


def create_commission_payout(statement):
    """
    Create a payout for a Posted Commission Statement.
    """

    # Always work with the latest database state.
    statement = frappe.get_doc(
        "Commission Statement",
        statement.name,
    )

    if statement.status != "Posted":
        frappe.throw(
            f"Commission Payout can only be created "
            f"for a Posted Commission Statement. "
            f"Current status: '{statement.status}'.",
            title="Statement Not Ready for Payout",
        )

    if (statement.net_commission or 0) <= 0:
        frappe.throw(
            "Cannot create a payout for a Commission Statement "
            "with zero or negative net commission.",
            title="Invalid Payout Amount",
        )

    existing_payout = frappe.get_all(
        "Commission Payout",
        filters={
            "commission_statement": statement.name,
            "status": ["!=", "Cancelled"],
        },
        fields=["name", "status"],
        limit=1,
    )

    if existing_payout:
        frappe.throw(
            f"An active Commission Payout "
            f"'{existing_payout[0].name}' already exists "
            f"for statement '{statement.name}'.",
            title="Payout Already Exists",
        )

    payout = frappe.get_doc(
        {
            "doctype": "Commission Payout",
            "commission_statement": statement.name,
            "commission_payee": statement.commission_payee,
            "company": statement.company,
            "currency": statement.currency,
            "amount": statement.net_commission,
            "status": "Pending",
        }
    )

    payout.insert()

    return payout


@frappe.whitelist()
def create_payout_from_statement(statement_name):
    require_role("Commission Payout Manager")

    statement = frappe.get_doc(
        "Commission Statement",
        statement_name,
    )

    payout = create_commission_payout(statement)

    return payout.name
