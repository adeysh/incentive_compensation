// Copyright (c) 2026, Adesh Katiya and contributors
// For license information, please see license.txt

frappe.ui.form.on("Commission Statement", {
	refresh(frm) {
		if (frm.is_new()) {
			frm.add_custom_button(__("Generate Statement"), () => {
				generate_commission_statement(frm);
			});

			return;
		}

		add_workflow_buttons(frm);
	},
});

function generate_commission_statement(frm) {
	if (!frm.doc.commission_payee) {
		frappe.msgprint(__("Please select a Commission Payee."));
		return;
	}

	if (!frm.doc.company) {
		frappe.msgprint(__("Please select a Company."));
		return;
	}

	if (!frm.doc.currency) {
		frappe.msgprint(__("Please select a Currency."));
		return;
	}

	if (!frm.doc.from_date) {
		frappe.msgprint(__("Please select a From Date."));
		return;
	}

	if (!frm.doc.to_date) {
		frappe.msgprint(__("Please select a To Date."));
		return;
	}

	frappe.call({
		method: "incentive_compensation.incentive_compensation.commission_engine.statement.generate_commission_statement",
		args: {
			commission_payee: frm.doc.commission_payee,
			company: frm.doc.company,
			currency: frm.doc.currency,
			from_date: frm.doc.from_date,
			to_date: frm.doc.to_date,
		},
		freeze: true,
		freeze_message: __("Generating Commission Statement..."),
		callback(response) {
			if (!response.message) {
				return;
			}

			frappe.set_route("Form", "Commission Statement", response.message);
		},
	});
}

function add_workflow_buttons(frm) {
	if (frm.doc.status === "Generated") {
		frm.add_custom_button(__("Submit for Review"), () => {
			confirm_transition(
				frm,
				__("Submit this Commission Statement for review?"),
				"submit_statement_for_review",
			);
		});
	}

	if (frm.doc.status === "Under Review") {
		frm.add_custom_button(__("Approve"), () => {
			confirm_transition(frm, __("Approve this Commission Statement?"), "approve_statement");
		});
	}

	if (frm.doc.status === "Approved") {
		frm.add_custom_button(__("Post"), () => {
			confirm_transition(frm, __("Post this Commission Statement?"), "post_statement");
		});
	}

	if (frm.doc.status === "Posted") {
		frm.add_custom_button(__("Create Payout"), () => {
			create_commission_payout(frm);
		});
	}
}

function confirm_transition(frm, message, method) {
	frappe.confirm(message, () => {
		frappe.call({
			method:
				"incentive_compensation.incentive_compensation.commission_engine.statement_workflow." +
				method,
			args: {
				statement_name: frm.doc.name,
			},
			freeze: true,
			freeze_message: __("Updating Commission Statement..."),
			callback() {
				frm.reload_doc();
			},
		});
	});
}

function create_commission_payout(frm) {
	frappe.confirm(__("Create a Commission Payout for this statement?"), () => {
		frappe.call({
			method: "incentive_compensation.incentive_compensation.commission_engine.payout.create_payout_from_statement",
			args: {
				statement_name: frm.doc.name,
			},
			freeze: true,
			freeze_message: __("Creating Commission Payout..."),
			callback(response) {
				if (!response.message) {
					return;
				}

				frappe.set_route("Form", "Commission Payout", response.message);
			},
		});
	});
}
