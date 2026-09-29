import frappe
from frappe.utils import now_datetime

from .statement_resolver import get_statement_ledger_entries


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
    entries = get_statement_ledger_entries(
        commission_payee,
        company,
        currency,
        from_date,
        to_date,
    )

    if not entries:
        frappe.throw(
            "No eligible Commission Ledger entries found "
            "for the selected payee and date range.",
            title="No Commission Entries",
        )

    totals = calculate_statement_totals(entries)

    statement = frappe.get_doc(
        {
            "doctype": "Commission Statement",
            "commission_payee": commission_payee,
            "company": company,
            "currency": currency,
            "from_date": from_date,
            "to_date": to_date,
            "gross_commission": totals["gross_commission"],
            "adjustments": totals["adjustments"],
            "net_commission": totals["net_commission"],
            "generation_date": now_datetime(),
            "status": "Generated",
        }
    )

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

    statement.insert()

    return statement


@frappe.whitelist()
def generate_commission_statement(
    commission_payee,
    company,
    currency,
    from_date,
    to_date,
):
    statement = create_commission_statement(
        commission_payee=commission_payee,
        company=company,
        currency=currency,
        from_date=from_date,
        to_date=to_date,
    )

    return statement.name
