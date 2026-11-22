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


def get_statement_opening_balance(statement):
    """Validate statement order and resolve the previous negative balance."""

    from_date = getdate(statement.from_date)
    to_date = getdate(statement.to_date)

    if from_date > to_date:
        frappe.throw(
            "From Date cannot be after To Date.",
            title="Invalid Statement Period",
        )

    existing_statements = frappe.get_all(
        "Commission Statement",
        filters={
            "commission_payee": statement.commission_payee,
            "company": statement.company,
            "currency": statement.currency,
            "status": ["!=", "Cancelled"],
            "name": ["!=", statement.name],
        },
        fields=[
            "name",
            "from_date",
            "to_date",
            "status",
            "closing_balance",
            "net_commission",
        ],
        order_by="to_date desc, from_date desc",
    )

    previous_statements = []

    for existing in existing_statements:
        # Prevent overlapping statement periods.
        if (
            getdate(existing.from_date) <= to_date
            and getdate(existing.to_date) >= from_date
        ):
            frappe.throw(
                f"Statement period overlaps with {existing.name}.",
                title="Overlapping Statement Period",
            )

        # Every earlier statement must be finalized or cancelled.
        if getdate(existing.to_date) < from_date:
            if existing.status != "Posted":
                frappe.throw(
                    f"Previous statement {existing.name} is not Posted. "
                    "Complete or cancel it before generating this statement.",
                    title="Previous Statement Not Finalized",
                )

            previous_statements.append(existing)

        # Do not generate an earlier period after a later one is Posted.
        if getdate(existing.from_date) > to_date and existing.status == "Posted":
            frappe.throw(
                f"Later statement {existing.name} is already Posted. "
                "Statements must be generated in chronological order.",
                title="Invalid Statement Order",
            )

    if not previous_statements:
        return 0

    previous = previous_statements[0]

    closing_balance = previous.closing_balance or 0

    # Handle statements generated before balance tracking was introduced.
    # Older records have zero-valued balance fields after migration.

    if (
        closing_balance == 0
        and (previous.net_commission or 0) < 0
        and (previous.opening_balance or 0) == 0
        and (previous.payable_amount or 0) == 0
    ):
        closing_balance = previous.net_commission

    return min(closing_balance, 0)
