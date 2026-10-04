# Copyright (c) 2026, Adesh Katiya and contributors
# For license information, please see license.txt

from incentive_compensation.incentive_compensation.commission_engine.reports.commission_reports import (
    get_commission_by_plan,
)


def execute(filters=None):
    filters = filters or {}

    columns = [
        {
            "label": "Commission Plan",
            "fieldname": "commission_plan",
            "fieldtype": "Link",
            "options": "Commission Plan",
            "width": 220,
        },
        {
            "label": "Gross Commission",
            "fieldname": "gross_commission",
            "fieldtype": "Currency",
            "width": 160,
        },
        {
            "label": "Adjustments",
            "fieldname": "adjustments",
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "label": "Net Commission",
            "fieldname": "net_commission",
            "fieldtype": "Currency",
            "width": 160,
        },
    ]

    data = get_commission_by_plan(
        company=filters.get("company"),
        commission_plan=filters.get("commission_plan"),
        from_date=filters.get("from_date"),
        to_date=filters.get("to_date"),
    )

    return columns, data
