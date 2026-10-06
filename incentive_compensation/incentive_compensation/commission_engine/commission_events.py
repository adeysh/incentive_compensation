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

    old_status = frappe.db.get_value(
        "Commission Statement",
        doc.name,
        "status",
    )

    if not old_status:
        return

    if doc.status == old_status:
        return

    # Draft → Generated is performed by the
    # controlled statement-generation operation.
    if (
        old_status == "Draft"
        and doc.status == "Generated"
        and getattr(doc.flags, "generating", False)
    ):
        return

    # All other status changes must go through
    # the statement workflow.
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
