import frappe

from .ledger import (
    create_ledger_entries_for_invoice,
    reverse_commissions_for_invoice,
)


def on_sales_invoice_submit(doc, method=None):
    create_ledger_entries_for_invoice(doc)


def on_sales_invoice_cancel(doc, method=None):
    reverse_commissions_for_invoice(doc)


def validate_commission_statement(doc, method=None):
    if doc.is_new():
        return

    old_doc = frappe.get_doc(
        "Commission Statement",
        doc.name,
    )

    old_status = old_doc.status

    if not old_status:
        return

    # Status changes must go through the statement workflow.
    if doc.status != old_status:
        from .statement_workflow import VALID_TRANSITIONS

        allowed_statuses = VALID_TRANSITIONS.get(
            old_status,
            set(),
        )

        if not getattr(
            doc.flags,
            "allow_statement_transition",
            False,
        ):
            frappe.throw(
                f"Commission Statement status cannot be "
                f"changed directly from '{old_status}' to "
                f"'{doc.status}'. Use the statement workflow.",
                title="Use Statement Workflow",
            )

        if doc.status not in allowed_statuses:
            frappe.throw(
                f"Cannot change Commission Statement "
                f"from '{old_status}' to '{doc.status}'.",
                title="Invalid Statement Transition",
            )

    # A generated statement is a financial snapshot.
    # Its contents cannot be changed after creation.
    protected_fields = [
        "commission_payee",
        "company",
        "currency",
        "from_date",
        "to_date",
        "gross_commission",
        "adjustments",
        "net_commission",
        "generation_date",
    ]

    for field in protected_fields:
        if doc.get(field) != old_doc.get(field):
            frappe.throw(
                f"Field '{field}' cannot be changed "
                f"after the Commission Statement has been generated.",
                title="Statement Field Locked",
            )

    # Ledger entries are part of the immutable snapshot.
    old_entries = {
        row.name: {
            "commission_ledger": row.commission_ledger,
            "sales_invoice": row.sales_invoice,
            "transaction_date": row.transaction_date,
            "commission_amount": row.commission_amount,
            "entry_type": row.entry_type,
        }
        for row in old_doc.ledger_entries
    }

    new_entries = {
        row.name: {
            "commission_ledger": row.commission_ledger,
            "sales_invoice": row.sales_invoice,
            "transaction_date": row.transaction_date,
            "commission_amount": row.commission_amount,
            "entry_type": row.entry_type,
        }
        for row in doc.ledger_entries
    }

    if old_entries != new_entries:
        frappe.throw(
            "Ledger Entries cannot be added, removed, "
            "or modified after the Commission Statement "
            "has been generated.",
            title="Ledger Entries Locked",
        )


def validate_commission_payout(doc, method=None):
    if doc.is_new():
        return

    old_values = frappe.db.get_value(
        "Commission Payout",
        doc.name,
        [
            "status",
            "commission_statement",
            "commission_payee",
            "company",
            "currency",
            "amount",
        ],
        as_dict=True,
    )

    if not old_values:
        return

    old_status = old_values.status

    # 1. Validate status transition

    if doc.status != old_status:
        from .payout_workflow import VALID_TRANSITIONS

        allowed_statuses = VALID_TRANSITIONS.get(
            old_status,
            set(),
        )

        if not getattr(
            doc.flags,
            "allow_payout_transition",
            False,
        ):
            frappe.throw(
                f"Commission Payout status cannot be "
                f"changed directly from '{old_status}' to "
                f"'{doc.status}'. Use the payout workflow.",
                title="Use Payout Workflow",
            )

        if doc.status not in allowed_statuses:
            frappe.throw(
                f"Cannot change Commission Payout "
                f"from '{old_status}' to '{doc.status}'.",
                title="Invalid Payout Transition",
            )

    # 2. Protect financial identity after processing starts

    if old_status in {"Processing", "Paid"}:
        protected_fields = [
            "commission_statement",
            "commission_payee",
            "company",
            "currency",
            "amount",
        ]

        for field in protected_fields:
            if doc.get(field) != old_values.get(field):
                frappe.throw(
                    f"Field '{field}' cannot be changed "
                    f"after payout processing has started.",
                    title="Payout Field Locked",
                )
