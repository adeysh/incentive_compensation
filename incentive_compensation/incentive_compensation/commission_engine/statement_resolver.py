import frappe
from frappe.utils import getdate


def get_statement_ledger_entries(
    commission_payee,
    company,
    currency,
    from_date,
    to_date,
):
    from_date = getdate(from_date)
    to_date = getdate(to_date)

    if from_date > to_date:
        frappe.throw(
            "From Date cannot be after To Date.",
            title="Invalid Statement Period",
        )

    entries = frappe.get_all(
        "Commission Ledger",
        filters={
            "commission_payee": commission_payee,
            "company": company,
            "currency": currency,
            "transaction_date": [
                "between",
                [from_date, to_date],
            ],
            "status": [
                "in",
                [
                    "Calculated",
                    "Under Review",
                    "Approved",
                    "Posted",
                ],
            ],
        },
        fields=[
            "name",
            "sales_invoice",
            "commission_payee",
            "commission_rule",
            "commission_plan",
            "commission_amount",
            "base_amount",
            "transaction_date",
            "entry_type",
            "status",
        ],
        order_by="transaction_date asc, name asc",
    )

    statement_entries = []

    for entry in entries:
        already_stated = frappe.db.sql(
            """
            SELECT cse.name
            FROM `tabCommission Statement Entry` cse
            INNER JOIN `tabCommission Statement` cs
                ON cs.name = cse.parent
            WHERE cse.commission_ledger = %s
            AND cse.parenttype = 'Commission Statement'
            AND cs.status != 'Cancelled'
            LIMIT 1
            """,
            entry.name,
        )

        if already_stated:
            continue

        statement_entries.append(entry)

    return statement_entries
