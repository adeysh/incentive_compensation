# Copyright (c) 2026, Adesh Katiya and contributors
# For license information, please see license.txt

from frappe import _

from incentive_compensation.incentive_compensation.commission_engine.reports.commission_reports import (
    get_commission_by_invoice,
)


def execute(filters=None):
    filters = filters or {}

    columns = get_columns()

    data = get_commission_by_invoice(
        company=filters.get("company"),
        sales_invoice=filters.get("sales_invoice"),
        from_date=filters.get("from_date"),
        to_date=filters.get("to_date"),
    )

    return columns, data


def get_columns():
    return [
        {
            "label": _("Sales Invoice"),
            "fieldname": "sales_invoice",
            "fieldtype": "Link",
            "options": "Sales Invoice",
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
