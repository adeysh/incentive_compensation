# Copyright (c) 2026, Adesh Katiya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

IMMUTABLE_FIELDS = [
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


class CommissionStatement(Document):
    def validate(self):
        self.validate_immutable_fields()

    def validate_immutable_fields(self):
        if self.is_new():
            return

        old_values = frappe.db.get_value(
            "Commission Statement",
            self.name,
            IMMUTABLE_FIELDS,
            as_dict=True,
        )

        if not old_values:
            return

        for field in IMMUTABLE_FIELDS:
            if self.get(field) != old_values.get(field):
                frappe.throw(
                    f"Commission Statement field '{field}' "
                    "cannot be changed after generation.",
                    title="Commission Statement Is Immutable",
                )
