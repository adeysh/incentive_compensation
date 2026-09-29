import frappe

VALID_TRANSITIONS = {
    "Pending": {"Processing", "Cancelled"},
    "Processing": {"Paid", "Failed"},
    "Failed": {"Processing", "Cancelled"},
}


def transition_payout(payout, new_status):
    payout = frappe.get_doc(
        "Commission Payout",
        payout.name,
    )

    current_status = payout.status

    allowed_statuses = VALID_TRANSITIONS.get(
        current_status,
        set(),
    )

    if new_status not in allowed_statuses:
        frappe.throw(
            f"Cannot change Commission Payout "
            f"from '{current_status}' to '{new_status}'.",
            title="Invalid Payout Transition",
        )

    if new_status == "Paid":
        if not payout.payment_date:
            frappe.throw(
                "Payment Date is required when a payout is marked Paid.",
                title="Payment Date Required",
            )

        if not payout.payment_reference:
            frappe.throw(
                "Payment Reference is required when a payout is marked Paid.",
                title="Payment Reference Required",
            )

    payout.flags.allow_payout_transition = True
    payout.status = new_status
    payout.save()

    if new_status == "Paid":
        from .statement_workflow import mark_statement_paid

        mark_statement_paid(payout.commission_statement)

    return payout


def start_payout_processing(payout):
    return transition_payout(
        payout,
        "Processing",
    )


def mark_payout_paid(payout):
    return transition_payout(
        payout,
        "Paid",
    )


def mark_payout_failed(payout):
    return transition_payout(
        payout,
        "Failed",
    )


def retry_payout(payout):
    return transition_payout(
        payout,
        "Processing",
    )


def cancel_payout(payout):
    return transition_payout(
        payout,
        "Cancelled",
    )


@frappe.whitelist()
def start_payout_processing(payout_name):
    payout = frappe.get_doc(
        "Commission Payout",
        payout_name,
    )

    return transition_payout(
        payout,
        "Processing",
    )


@frappe.whitelist()
def mark_payout_paid(payout_name):
    payout = frappe.get_doc(
        "Commission Payout",
        payout_name,
    )

    return transition_payout(
        payout,
        "Paid",
    )


@frappe.whitelist()
def mark_payout_failed(payout_name):
    payout = frappe.get_doc(
        "Commission Payout",
        payout_name,
    )

    return transition_payout(
        payout,
        "Failed",
    )


@frappe.whitelist()
def retry_payout(payout_name):
    payout = frappe.get_doc(
        "Commission Payout",
        payout_name,
    )

    return transition_payout(
        payout,
        "Processing",
    )


@frappe.whitelist()
def cancel_payout(payout_name):
    payout = frappe.get_doc(
        "Commission Payout",
        payout_name,
    )

    return transition_payout(
        payout,
        "Cancelled",
    )
