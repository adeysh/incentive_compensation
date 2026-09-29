// Copyright (c) 2026, Adesh Katiya and contributors
// For license information, please see license.txt

frappe.query_reports["Commission by Date"] = {
	filters: [
		{
			fieldname: "company",
			label: "Company",
			fieldtype: "Link",
			options: "Company",
			reqd: 1,
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "from_date",
			label: "From Date",
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.month_start(),
		},
		{
			fieldname: "to_date",
			label: "To Date",
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.month_end(),
		},
	],
};
