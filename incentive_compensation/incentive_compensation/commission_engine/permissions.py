import frappe


def require_role(role):
    if role not in frappe.get_roles():
        frappe.throw(
            f"You must have the {role} role to perform this action.",
            title="Not Authorized",
        )


def get_commission_record_query(user):
    """Restrict Commission Users to records belonging to their payee."""

    if not user or user == "Administrator":
        return ""

    roles = frappe.get_roles(user)

    # Managers retain access according to their DocType permissions.
    manager_roles = {
        "System Manager",
        "Commission Manager",
        "Commission Payout Manager",
    }

    if manager_roles.intersection(roles):
        return ""

    if "Commission User" not in roles:
        return ""

    escaped_user = frappe.db.escape(user)

    return f"""
        commission_payee IN (
            SELECT name
            FROM `tabCommission Payee`
            WHERE user = {escaped_user}
            AND enabled = 1
        )
    """


def has_commission_record_permission(doc, ptype, user=None):
    """Check ownership when a Commission User opens an individual record."""

    user = user or frappe.session.user

    if not user or user == "Administrator":
        return None

    roles = frappe.get_roles(user)

    manager_roles = {
        "System Manager",
        "Commission Manager",
        "Commission Payout Manager",
    }

    if manager_roles.intersection(roles):
        return None

    if "Commission User" not in roles:
        return None

    # Commission Users are read-only. Other permissions remain governed
    # by the normal DocType permission system.
    if ptype != "read":
        return False

    if not doc.commission_payee:
        return False

    return bool(
        frappe.db.exists(
            "Commission Payee",
            {
                "name": doc.commission_payee,
                "user": user,
                "enabled": 1,
            },
        )
    )
