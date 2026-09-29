# Copyright (c) 2026, Adesh Katiya and contributors
# For license information, please see license.txt

from incentive_compensation.incentive_compensation.commission_engine.reports.commission_reports import (
    get_commission_by_payee,
)


def execute(filters=None):
    filters = filters or {}

    columns = [
        {
            "label": "Commission Payee",
            "fieldname": "commission_payee",
            "fieldtype": "Link",
            "options": "Commission Payee",
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

    data = get_commission_by_payee(
        company=filters.get("company"),
        from_date=filters.get("from_date"),
        to_date=filters.get("to_date"),
    )

    return columns, data
