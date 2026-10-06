// Copyright (c) 2026, Adesh Katiya and contributors
// For license information, please see license.txt

frappe.ui.form.on("Commission Statement", {
	refresh(frm) {
		set_statement_field_visibility(frm);
		set_statement_intro(frm);

		if (frm.is_new()) {
			return;
		}

		if (frm.doc.status === "Draft") {
			frm.add_custom_button(__("Generate Statement"), () => {
				generate_commission_statement(frm);
			});

			return;
		}

		add_workflow_buttons(frm);
	},
});

function set_statement_intro(frm) {
	if (!frm.is_new() && frm.doc.status === "Draft") {
		if (frm.__statement_intro_shown) {
			return;
		}

		frm.set_intro(
			__(
				"This statement is ready to generate. Generation will calculate eligible commissions for the selected payee and period and create an immutable snapshot.",
			),
			"blue",
		);

		frm.__statement_intro_shown = true;
		return;
	}

	// Clear the intro when the statement is no longer a Draft.
	frm.set_intro("");
	frm.__statement_intro_shown = false;
}

function set_statement_field_visibility(frm) {
	const generated = !frm.is_new() && frm.doc.status !== "Draft";

	frm.toggle_display("commission_section", generated);
	frm.toggle_display("generation_date", generated);
	frm.toggle_display("ledger_entries_section", generated);
}

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
			statement_name: frm.doc.name,
		},
		freeze: true,
		freeze_message: __("Generating Commission Statement..."),
		callback() {
			frm.reload_doc();
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
