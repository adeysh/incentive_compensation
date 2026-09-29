# Copyright (c) 2026, Adesh Katiya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime, getdate

IMMUTABLE_FIELDS = [
    "commission_amount",
    "rate",
    "base_amount",
    "commission_rule",
    "commission_plan",
    "commission_payee",
    "transaction_date",
    "calculation_method",
    "fixed_amount",
    "currency",
    "company",
    "sales_invoice_item",
    "sales_invoice",
    "source_key",
    "calculation_date",
    "entry_type",
    "reversal_of",
]


class CommissionLedger(Document):

    def validate(self):
        self.validate_calculation_fields()

    def on_trash(self):
        frappe.throw(
            "Commission Ledger entries cannot be deleted.",
            title="Commission Ledger Is Immutable",
        )

    def before_rename(self, olddn, newdn, merge=False):
        frappe.throw(
            "Commission Ledger entries cannot be renamed.",
            title="Commission Ledger Is Immutable",
        )

    def _values_equal(self, field, current_value, old_value):
        fieldtype = self.meta.get_field(field).fieldtype

        if fieldtype == "Date":
            return getdate(current_value) == getdate(old_value)

        if fieldtype == "Datetime":
            return get_datetime(current_value) == get_datetime(old_value)

        return current_value == old_value

    def validate_calculation_fields(self):
        if self.is_new():
            return

        old_values = frappe.db.get_value(
            "Commission Ledger",
            self.name,
            IMMUTABLE_FIELDS,
            as_dict=True,
        )

        if not old_values:
            return

        for field in IMMUTABLE_FIELDS:
            if not self._values_equal(
                field,
                self.get(field),
                old_values.get(field),
            ):
                frappe.throw(
                    f"Commission Ledger field '{field}' "
                    "cannot be changed after creation.",
                    title="Commission Ledger Is Immutable",
                )
