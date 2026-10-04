# Copyright (c) 2026, Adesh Katiya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

IMMUTABLE_AFTER_PROCESSING = [
    "commission_statement",
    "commission_payee",
    "company",
    "currency",
    "amount",
]


class CommissionPayout(Document):

    def validate(self):
        self.validate_status_change()
        self.validate_locked_fields()

    def validate_status_change(self):
        if self.is_new():
            return

        old_status = frappe.db.get_value(
            "Commission Payout",
            self.name,
            "status",
        )

        if old_status == self.status:
            return

        if not getattr(
            self.flags,
            "allow_payout_transition",
            False,
        ):
            frappe.throw(
                "Commission Payout status can only be "
                "changed through the payout workflow.",
                title="Invalid Payout Status Change",
            )

        from incentive_compensation.incentive_compensation.commission_engine.payout_workflow import (
            VALID_TRANSITIONS,
        )

        allowed_statuses = VALID_TRANSITIONS.get(
            old_status,
            set(),
        )

        if self.status not in allowed_statuses:
            frappe.throw(
                f"Cannot change Commission Payout "
                f"from '{old_status}' to '{self.status}'.",
                title="Invalid Payout Transition",
            )

    def validate_locked_fields(self):
        if self.is_new():
            return

        old_doc = frappe.db.get_value(
            "Commission Payout",
            self.name,
            [
                "status",
                *IMMUTABLE_AFTER_PROCESSING,
                "payment_reference",
                "payment_date",
            ],
            as_dict=True,
        )

        if not old_doc:
            return

        if old_doc.status == "Processing":
            for field in IMMUTABLE_AFTER_PROCESSING:
                if self.get(field) != old_doc.get(field):
                    frappe.throw(
                        f"Commission Payout field '{field}' "
                        "cannot be changed after processing.",
                        title="Commission Payout Is Locked",
                    )

        if old_doc.status == "Paid":
            locked_fields = [
                *IMMUTABLE_AFTER_PROCESSING,
                "payment_reference",
                "payment_date",
            ]

            for field in locked_fields:
                if self.get(field) != old_doc.get(field):
                    frappe.throw(
                        f"Commission Payout field '{field}' "
                        "cannot be changed after payment.",
                        title="Commission Payout Is Paid",
                    )
