import frappe


def require_role(role):
    if role not in frappe.get_roles():
        frappe.throw(
            f"You must have the {role} role to perform this action.",
            title="Not Authorized",
        )
