import frappe
from frappe.utils import now_datetime

from .statement_resolver import get_statement_ledger_entries
from .permissions import require_role


def calculate_statement_totals(entries):
    gross_commission = 0
    adjustments = 0

    for entry in entries:
        amount = entry.commission_amount or 0

        if entry.entry_type == "Commission":
            gross_commission += amount

        elif entry.entry_type in ("Adjustment", "Reversal"):
            adjustments += amount

    net_commission = gross_commission + adjustments

    return {
        "gross_commission": gross_commission,
        "adjustments": adjustments,
        "net_commission": net_commission,
    }


def create_commission_statement(
    commission_payee,
    company,
    currency,
    from_date,
    to_date,
):
    statement = frappe.get_doc(
        {
            "doctype": "Commission Statement",
            "commission_payee": commission_payee,
            "company": company,
            "currency": currency,
            "from_date": from_date,
            "to_date": to_date,
            "status": "Draft",
        }
    )

    statement.insert()

    return statement


def generate_statement(statement):
    if statement.status != "Draft":
        frappe.throw(
            "Only Draft Commission Statements can be generated.",
            title="Invalid Statement Status",
        )

    statement.flags.generating = True

    entries = get_statement_ledger_entries(
        statement.commission_payee,
        statement.company,
        statement.currency,
        statement.from_date,
        statement.to_date,
    )

    if not entries:
        frappe.throw(
            "No eligible Commission Ledger entries found "
            "for the selected payee and date range.",
            title="No Commission Entries",
        )

    totals = calculate_statement_totals(entries)

    statement.gross_commission = totals["gross_commission"]
    statement.adjustments = totals["adjustments"]
    statement.net_commission = totals["net_commission"]
    statement.generation_date = now_datetime()
    statement.status = "Generated"

    statement.set("ledger_entries", [])

    for entry in entries:
        statement.append(
            "ledger_entries",
            {
                "commission_ledger": entry.name,
                "sales_invoice": entry.sales_invoice,
                "transaction_date": entry.transaction_date,
                "commission_amount": entry.commission_amount,
                "entry_type": entry.entry_type,
            },
        )

    statement.save()

    return statement


@frappe.whitelist()
def generate_commission_statement(statement_name):
    require_role("Commission Manager")

    statement = frappe.get_doc("Commission Statement", statement_name)

    if statement.status != "Draft":
        frappe.throw(
            "Only Draft Commission Statements can be generated.",
            title="Invalid Statement Status",
        )

    generate_statement(statement)

    return statement.name
