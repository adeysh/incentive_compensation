// Copyright (c) 2026, Adesh Katiya and contributors
// For license information, please see license.txt

frappe.ui.form.on("Commission Payout", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		add_payout_buttons(frm);
	},
});

function add_payout_buttons(frm) {
	if (frm.doc.status === "Pending") {
		frm.add_custom_button(__("Start Processing"), () => {
			confirm_payout_transition(
				frm,
				__("Start processing this Commission Payout?"),
				"start_payout_processing",
			);
		});

		frm.add_custom_button(__("Cancel"), () => {
			confirm_payout_transition(frm, __("Cancel this Commission Payout?"), "cancel_payout");
		});
	}

	if (frm.doc.status === "Processing") {
		frm.add_custom_button(__("Mark as Paid"), () => {
			mark_payout_as_paid(frm);
		});

		frm.add_custom_button(__("Mark as Failed"), () => {
			confirm_payout_transition(
				frm,
				__("Mark this Commission Payout as failed?"),
				"mark_payout_failed",
			);
		});
	}

	if (frm.doc.status === "Failed") {
		frm.add_custom_button(__("Retry Processing"), () => {
			confirm_payout_transition(
				frm,
				__("Retry processing this Commission Payout?"),
				"retry_payout",
			);
		});

		frm.add_custom_button(__("Cancel"), () => {
			confirm_payout_transition(frm, __("Cancel this Commission Payout?"), "cancel_payout");
		});
	}
}

function confirm_payout_transition(frm, message, method) {
	frappe.confirm(message, () => {
		frappe.call({
			method:
				"incentive_compensation.incentive_compensation.commission_engine.payout_workflow." +
				method,
			args: {
				payout_name: frm.doc.name,
			},
			freeze: true,
			freeze_message: __("Updating Commission Payout..."),
			callback() {
				frm.reload_doc();
			},
		});
	});
}

function mark_payout_as_paid(frm) {
	if (!frm.doc.payment_date) {
		frappe.msgprint(__("Please enter a Payment Date before marking the payout as Paid."));
		return;
	}

	if (!frm.doc.payment_reference) {
		frappe.msgprint(__("Please enter a Payment Reference before marking the payout as Paid."));
		return;
	}

	frappe.confirm(__("Mark this Commission Payout as Paid?"), () => {
		frappe.call({
			method: "incentive_compensation.incentive_compensation.commission_engine.payout_workflow.mark_payout_paid",
			args: {
				payout_name: frm.doc.name,
			},
			freeze: true,
			freeze_message: __("Marking Commission Payout as Paid..."),
			callback() {
				frm.reload_doc();
			},
		});
	});
}
