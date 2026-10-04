import frappe
from .permissions import require_role

VALID_TRANSITIONS = {
    "Generated": {
        "Under Review",
    },
    "Under Review": {
        "Approved",
        "Cancelled",
    },
    "Approved": {
        "Posted",
        "Cancelled",
    },
    "Posted": {
        "Paid",
    },
}


def transition_statement(statement, new_status):
    statement = frappe.get_doc(
        "Commission Statement",
        statement.name,
    )

    current_status = statement.status

    allowed_statuses = VALID_TRANSITIONS.get(
        current_status,
        set(),
    )

    if new_status not in allowed_statuses:
        frappe.throw(
            f"Cannot change Commission Statement "
            f"from '{current_status}' to '{new_status}'.",
            title="Invalid Statement Transition",
        )

    statement.flags.allow_statement_transition = True
    statement.status = new_status
    statement.save()

    return statement


def submit_statement_for_review(statement):
    return transition_statement(
        statement,
        "Under Review",
    )


def approve_statement(statement):
    return transition_statement(
        statement,
        "Approved",
    )


def post_statement(statement):
    return transition_statement(
        statement,
        "Posted",
    )


def mark_statement_paid(statement):
    return transition_statement(
        statement,
        "Paid",
    )


@frappe.whitelist()
def cancel_statement(statement_name):
    require_role("Commission Manager")

    statement = frappe.get_doc(
        "Commission Statement",
        statement_name,
    )

    return transition_statement(
        statement,
        "Cancelled",
    )


@frappe.whitelist()
def submit_statement_for_review(statement_name):
    require_role("Commission Manager")

    statement = frappe.get_doc(
        "Commission Statement",
        statement_name,
    )

    return transition_statement(
        statement,
        "Under Review",
    )


@frappe.whitelist()
def approve_statement(statement_name):
    require_role("Commission Manager")

    statement = frappe.get_doc(
        "Commission Statement",
        statement_name,
    )

    return transition_statement(
        statement,
        "Approved",
    )


@frappe.whitelist()
def post_statement(statement_name):
    require_role("Commission Manager")

    statement = frappe.get_doc(
        "Commission Statement",
        statement_name,
    )

    return transition_statement(
        statement,
        "Posted",
    )


@frappe.whitelist()
def mark_statement_paid(statement_name):
    statement = frappe.get_doc(
        "Commission Statement",
        statement_name,
    )

    return transition_statement(
        statement,
        "Paid",
    )
