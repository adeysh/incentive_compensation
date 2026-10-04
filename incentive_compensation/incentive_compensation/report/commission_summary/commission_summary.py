# Copyright (c) 2026, Adesh Katiya and contributors
# For license information, please see license.txt

from frappe import _

from incentive_compensation.incentive_compensation.commission_engine.reports.commission_reports import (
    get_commission_by_payee,
)


def execute(filters=None):
    columns = get_columns()

    data = get_commission_by_payee(
        company=filters.get("company"),
        commission_payee=filters.get("commission_payee"),
        commission_plan=filters.get("commission_plan"),
        from_date=filters.get("from_date"),
        to_date=filters.get("to_date"),
    )

    return columns, data


def get_columns():
    return [
        {
            "label": _("Commission Payee"),
            "fieldname": "commission_payee",
            "fieldtype": "Link",
            "options": "Commission Payee",
            "width": 200,
        },
        {
            "label": _("Gross Commission"),
            "fieldname": "gross_commission",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": _("Adjustments"),
            "fieldname": "adjustments",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": _("Net Commission"),
            "fieldname": "net_commission",
            "fieldtype": "Currency",
            "width": 150,
        },
    ]
