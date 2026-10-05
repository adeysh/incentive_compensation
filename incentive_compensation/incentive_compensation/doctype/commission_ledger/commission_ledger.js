// Copyright (c) 2026, Adesh Katiya and contributors
// For license information, please see license.txt

frappe.ui.form.on("Commission Ledger", {
	refresh(frm) {
		frm.set_intro(
			__(
				"This commission ledger entry is an immutable audit record. It is generated automatically from the source transaction and cannot be edited or deleted.",
			),
			"blue",
		);
	},
});
