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
        self.validate_ledger_entries()

    def validate_immutable_fields(self):
        if self.is_new() or self.flags.generating:
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

    def validate_ledger_entries(self):
        if self.is_new() or self.flags.generating:
            return

        old_doc = frappe.get_doc(
            "Commission Statement",
            self.name,
        )

        old_entries = {
            row.name: {
                "commission_ledger": row.commission_ledger,
                "sales_invoice": row.sales_invoice,
                "transaction_date": row.transaction_date,
                "commission_amount": row.commission_amount,
                "entry_type": row.entry_type,
            }
            for row in old_doc.ledger_entries
        }

        new_entries = {
            row.name: {
                "commission_ledger": row.commission_ledger,
                "sales_invoice": row.sales_invoice,
                "transaction_date": row.transaction_date,
                "commission_amount": row.commission_amount,
                "entry_type": row.entry_type,
            }
            for row in self.ledger_entries
        }

        if old_entries != new_entries:
            frappe.throw(
                "Ledger Entries cannot be added, removed, "
                "or modified after the Commission Statement "
                "has been generated.",
                title="Ledger Entries Locked",
            )
