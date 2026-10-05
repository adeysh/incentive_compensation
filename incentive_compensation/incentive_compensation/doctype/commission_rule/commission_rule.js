// Copyright (c) 2026, Adesh Katiya and contributors
// For license information, please see license.txt

frappe.ui.form.on("Commission Rule", {
	based_on(frm) {
		const field_map = {
			Item: "item",
			"Item Group": "item_group",
			"Sales Person": "sales_person",
			Customer: "customer",
			"Customer Group": "customer_group",
			Territory: "territory",
		};

		Object.values(field_map).forEach((field) => {
			frm.set_value(field, null);
		});
	},

	calculation_method(frm) {
		if (frm.doc.calculation_method !== "Percentage") {
			frm.set_value("rate", null);
		}

		if (frm.doc.calculation_method !== "Fixed Amount") {
			frm.set_value("fixed_amount", null);
		}
	},
});
