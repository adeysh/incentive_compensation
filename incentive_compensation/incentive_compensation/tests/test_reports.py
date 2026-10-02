import frappe

from datetime import date
from erpnext.accounts.doctype.sales_invoice.test_sales_invoice import (
    create_sales_invoice,
)

from incentive_compensation.incentive_compensation.commission_engine.reports.commission_reports import (
    get_commission_by_payee,
    get_commission_by_plan,
    get_commission_by_rule,
    get_commission_by_invoice,
    get_commission_summary,
    get_commission_by_date,
)

from incentive_compensation.incentive_compensation.tests.test_base import (
    CommissionTestCase,
)

from incentive_compensation.incentive_compensation.report.commission_summary.commission_summary import (
    execute as execute_commission_summary,
)

from incentive_compensation.incentive_compensation.report.commission_by_date.commission_by_date import (
    execute as execute_commission_by_date,
)

from incentive_compensation.incentive_compensation.report.commission_by_invoice.commission_by_invoice import (
    execute as execute_commission_by_invoice,
)

from incentive_compensation.incentive_compensation.report.commission_by_payee.commission_by_payee import (
    execute as execute_commission_by_payee,
)

from incentive_compensation.incentive_compensation.report.commission_by_plan.commission_by_plan import (
    execute as execute_commission_by_plan,
)

from incentive_compensation.incentive_compensation.report.commission_by_rule.commission_by_rule import (
    execute as execute_commission_by_rule,
)


class TestCommissionReports(CommissionTestCase):

    @classmethod
    def _create_report_invoice(cls, posting_date, rate=1000):
        invoice = create_sales_invoice(
            company=cls.company,
            customer=cls.customer,
            debit_to=cls.debit_to,
            item=cls.item,
            qty=1,
            rate=rate,
            currency=cls.currency,
            posting_date=posting_date,
            parent_cost_center=cls.cost_center,
            cost_center=cls.cost_center,
            income_account=cls.income_account,
            do_not_submit=True,
        )

        invoice.append(
            "sales_team",
            {
                "sales_person": cls.sales_person,
                "allocated_percentage": 100,
            },
        )

        invoice.submit()

        return invoice

    @classmethod
    def _create_report_invoice_for_sales_person(
        cls,
        sales_person,
        posting_date,
        rate=1000,
        item=None,
    ):
        invoice = create_sales_invoice(
            company=cls.company,
            customer=cls.customer,
            debit_to=cls.debit_to,
            item=item or cls.item,
            qty=1,
            rate=rate,
            currency=cls.currency,
            posting_date=posting_date,
            parent_cost_center=cls.cost_center,
            cost_center=cls.cost_center,
            income_account=cls.income_account,
            do_not_submit=True,
        )

        invoice.append(
            "sales_team",
            {
                "sales_person": sales_person,
                "allocated_percentage": 100,
            },
        )

        invoice.submit()

        return invoice

    def test_commission_summary_aggregates_commission_entries(self):
        self._create_report_invoice(
            posting_date="2026-10-01",
            rate=1000,
        )

        result = get_commission_summary(
            company=self.company,
            from_date="2026-10-01",
            to_date="2026-10-01",
        )

        self.assertEqual(result["gross_commission"], 100)
        self.assertEqual(result["adjustments"], 0)
        self.assertEqual(result["net_commission"], 100)

    def test_commission_summary_filters_by_date(self):
        self._create_report_invoice(
            posting_date="2026-09-29",
            rate=1000,
        )

        self._create_report_invoice(
            posting_date="2026-09-30",
            rate=2000,
        )

        result = get_commission_summary(
            company=self.company,
            from_date="2026-09-29",
            to_date="2026-09-29",
        )

        self.assertEqual(result["gross_commission"], 100)
        self.assertEqual(result["adjustments"], 0)
        self.assertEqual(result["net_commission"], 100)

    def test_commission_summary_filters_by_company(self):
        self._create_report_invoice(
            posting_date="2026-09-27",
            rate=1000,
        )

        other_company = frappe.db.get_value(
            "Company",
            {"name": ["!=", self.company]},
            "name",
        )

        self.assertTrue(
            other_company,
            "Test requires another company besides the commission test company.",
        )

        result = get_commission_summary(
            company=other_company,
            from_date="2026-09-27",
            to_date="2026-09-27",
        )

        self.assertEqual(result["gross_commission"], 0)
        self.assertEqual(result["adjustments"], 0)
        self.assertEqual(result["net_commission"], 0)

    def test_commission_by_payee_groups_commissions(self):
        self._create_report_invoice_for_sales_person(
            sales_person=self.sales_person,
            posting_date="2026-09-25",
            rate=1000,
        )

        self._create_report_invoice_for_sales_person(
            sales_person=self.allocation_sales_person,
            posting_date="2026-09-26",
            rate=2000,
        )

        result = get_commission_by_payee(
            company=self.company,
            from_date="2026-09-25",
            to_date="2026-09-26",
        )

        results_by_payee = {row["commission_payee"]: row for row in result}

        self.assertIn(self.payee.name, results_by_payee)
        self.assertIn(self.allocation_payee.name, results_by_payee)

        self.assertEqual(
            results_by_payee[self.payee.name]["gross_commission"],
            100,
        )

        self.assertEqual(
            results_by_payee[self.allocation_payee.name]["gross_commission"],
            200,
        )

    def test_commission_by_plan_groups_commissions(self):
        base_plan = frappe.get_doc(
            {
                "doctype": "Commission Plan",
                "plan_name": "E2E Report Base Plan",
                "company": self.company,
                "currency": self.currency,
                "valid_from": "2026-11-01",
                "status": "Active",
            }
        )
        base_plan.insert()

        newer_plan = frappe.get_doc(
            {
                "doctype": "Commission Plan",
                "plan_name": "E2E Report Newer Plan",
                "company": self.company,
                "currency": self.currency,
                "valid_from": "2026-11-02",
                "status": "Active",
            }
        )
        newer_plan.insert()

        base_rule = frappe.get_doc(
            {
                "doctype": "Commission Rule",
                "rule_name": "E2E Report Base Rule",
                "commission_plan": base_plan.name,
                "priority": 100,
                "based_on": "Item",
                "item": self.item,
                "calculation_method": "Percentage",
                "rate": 10,
                "enabled": 1,
            }
        )
        base_rule.insert()

        newer_rule = frappe.get_doc(
            {
                "doctype": "Commission Rule",
                "rule_name": "E2E Report Newer Rule",
                "commission_plan": newer_plan.name,
                "priority": 100,
                "based_on": "Item",
                "item": self.priority_item,
                "calculation_method": "Percentage",
                "rate": 20,
                "enabled": 1,
            }
        )
        newer_rule.insert()

        self._create_report_invoice_for_sales_person(
            sales_person=self.sales_person,
            posting_date="2026-11-01",
            rate=1000,
            item=self.item,
        )

        self._create_report_invoice_for_sales_person(
            sales_person=self.sales_person,
            posting_date="2026-11-02",
            rate=2000,
            item=self.priority_item,
        )

        result = get_commission_by_plan(
            company=self.company,
            from_date="2026-11-01",
            to_date="2026-11-02",
        )

        results_by_plan = {row["commission_plan"]: row for row in result}

        self.assertIn(base_plan.name, results_by_plan)
        self.assertIn(newer_plan.name, results_by_plan)

        self.assertEqual(
            results_by_plan[base_plan.name]["gross_commission"],
            100,
        )

        self.assertEqual(
            results_by_plan[newer_plan.name]["gross_commission"],
            400,
        )

    def test_commission_by_rule_groups_commissions(self):
        self._create_report_invoice_for_sales_person(
            sales_person=self.sales_person,
            posting_date="2026-09-23",
            rate=1000,
            item=self.item,
        )

        self._create_report_invoice_for_sales_person(
            sales_person=self.sales_person,
            posting_date="2026-09-24",
            rate=1000,
            item=self.fixed_amount_item,
        )

        result = get_commission_by_rule(
            company=self.company,
            from_date="2026-09-23",
            to_date="2026-09-24",
        )

        results_by_rule = {row["commission_rule"]: row for row in result}

        self.assertIn(self.rule.name, results_by_rule)
        self.assertIn(self.fixed_amount_rule.name, results_by_rule)

        self.assertEqual(
            results_by_rule[self.rule.name]["gross_commission"],
            100,
        )

        self.assertEqual(
            results_by_rule[self.fixed_amount_rule.name]["gross_commission"],
            250,
        )

    def test_commission_by_invoice_groups_commissions(self):
        invoice_one = self._create_report_invoice_for_sales_person(
            sales_person=self.sales_person,
            posting_date="2026-09-20",
            rate=1000,
            item=self.item,
        )

        invoice_two = self._create_report_invoice_for_sales_person(
            sales_person=self.sales_person,
            posting_date="2026-09-21",
            rate=1000,
            item=self.fixed_amount_item,
        )

        result = get_commission_by_invoice(
            company=self.company,
            from_date="2026-09-20",
            to_date="2026-09-21",
        )

        results_by_invoice = {row["sales_invoice"]: row for row in result}

        self.assertIn(invoice_one.name, results_by_invoice)
        self.assertIn(invoice_two.name, results_by_invoice)

        self.assertEqual(
            results_by_invoice[invoice_one.name]["gross_commission"],
            100,
        )

        self.assertEqual(
            results_by_invoice[invoice_two.name]["gross_commission"],
            250,
        )

    def test_commission_by_date_groups_commissions(self):
        self._create_report_invoice_for_sales_person(
            sales_person=self.sales_person,
            posting_date="2026-09-18",
            rate=1000,
            item=self.item,
        )

        self._create_report_invoice_for_sales_person(
            sales_person=self.sales_person,
            posting_date="2026-09-19",
            rate=1000,
            item=self.fixed_amount_item,
        )

        result = get_commission_by_date(
            company=self.company,
            from_date="2026-09-18",
            to_date="2026-09-19",
        )

        results_by_date = {str(row["transaction_date"]): row for row in result}

        self.assertIn("2026-09-18", results_by_date)
        self.assertIn("2026-09-19", results_by_date)

        self.assertEqual(
            results_by_date["2026-09-18"]["gross_commission"],
            100,
        )

        self.assertEqual(
            results_by_date["2026-09-19"]["gross_commission"],
            250,
        )

    def test_commission_summary_handles_reversal(self):
        invoice = self._create_report_invoice_for_sales_person(
            sales_person=self.cancellation_sales_person,
            posting_date="2026-09-17",
            rate=1000,
            item=self.item,
        )

        ledger_entries = frappe.get_all(
            "Commission Ledger",
            filters={
                "sales_invoice": invoice.name,
                "entry_type": "Commission",
            },
            fields=["name"],
        )

        self.assertEqual(len(ledger_entries), 1)

        original_ledger = frappe.get_doc(
            "Commission Ledger",
            ledger_entries[0].name,
        )

        from incentive_compensation.incentive_compensation.commission_engine.ledger import (
            reverse_ledger_entry,
        )

        reverse_ledger_entry(original_ledger)

        result = get_commission_summary(
            company=self.company,
            commission_payee=self.cancellation_payee.name,
            from_date="2026-09-17",
            to_date="2026-10-02",
        )

        self.assertEqual(result["gross_commission"], 100)
        self.assertEqual(result["adjustments"], -100)
        self.assertEqual(result["net_commission"], 0)

    def test_commission_by_payee_handles_reversal(self):
        sales_person = self._create_sales_person("E2E Payee Reversal Sales Person")

        payee = self._create_payee(
            "E2E Payee Reversal Commission Payee",
            sales_person,
        )

        invoice = create_sales_invoice(
            company=self.company,
            customer=self.customer,
            debit_to=self.debit_to,
            item=self.item,
            qty=1,
            rate=1000,
            currency=self.currency,
            posting_date="2026-09-17",
            parent_cost_center=self.cost_center,
            cost_center=self.cost_center,
            income_account=self.income_account,
            do_not_submit=True,
        )

        invoice.append(
            "sales_team",
            {
                "sales_person": sales_person,
                "allocated_percentage": 100,
            },
        )

        invoice.submit()
        invoice.cancel()

        result = get_commission_by_payee(
            company=self.company,
            from_date="2026-09-17",
            to_date="2026-10-02",
        )

        rows = [row for row in result if row["commission_payee"] == payee.name]

        self.assertEqual(len(rows), 1)

        row = rows[0]

        self.assertEqual(row["gross_commission"], 100)
        self.assertEqual(row["adjustments"], -100)
        self.assertEqual(row["net_commission"], 0)

    def test_commission_summary_script_report(self):
        sales_person = self._create_sales_person(
            "E2E Summary Script Report Sales Person"
        )

        payee = self._create_payee(
            "E2E Summary Script Report Payee",
            sales_person,
        )

        invoice = create_sales_invoice(
            company=self.company,
            customer=self.customer,
            debit_to=self.debit_to,
            item=self.item,
            qty=1,
            rate=1000,
            currency=self.currency,
            posting_date="2026-10-02",
            parent_cost_center=self.cost_center,
            cost_center=self.cost_center,
            income_account=self.income_account,
            do_not_submit=True,
        )

        invoice.append(
            "sales_team",
            {
                "sales_person": sales_person,
                "allocated_percentage": 100,
            },
        )

        invoice.submit()

        columns, data = execute_commission_summary(
            {
                "company": self.company,
                "from_date": "2026-10-02",
                "to_date": "2026-10-02",
            }
        )

        column_fieldnames = [column["fieldname"] for column in columns]

        self.assertEqual(
            column_fieldnames,
            [
                "commission_payee",
                "gross_commission",
                "adjustments",
                "net_commission",
            ],
        )

        rows = [row for row in data if row["commission_payee"] == payee.name]

        self.assertEqual(len(rows), 1)

        row = rows[0]

        self.assertEqual(row["gross_commission"], 100)
        self.assertEqual(row["adjustments"], 0)
        self.assertEqual(row["net_commission"], 100)

    def test_commission_by_date_script_report(self):
        sales_person = self._create_sales_person("E2E Date Script Report Sales Person")

        payee = self._create_payee(
            "E2E Date Script Report Payee",
            sales_person,
        )

        invoice = create_sales_invoice(
            company=self.company,
            customer=self.customer,
            debit_to=self.debit_to,
            item=self.item,
            qty=1,
            rate=1000,
            currency=self.currency,
            posting_date="2026-10-02",
            parent_cost_center=self.cost_center,
            cost_center=self.cost_center,
            income_account=self.income_account,
            do_not_submit=True,
        )

        invoice.append(
            "sales_team",
            {
                "sales_person": sales_person,
                "allocated_percentage": 100,
            },
        )

        invoice.submit()

        columns, data = execute_commission_by_date(
            {
                "company": self.company,
                "from_date": "2026-10-02",
                "to_date": "2026-10-02",
            }
        )

        column_fieldnames = [column["fieldname"] for column in columns]

        self.assertEqual(
            column_fieldnames,
            [
                "transaction_date",
                "gross_commission",
                "adjustments",
                "net_commission",
            ],
        )

        rows = [row for row in data if row["transaction_date"] == date(2026, 10, 2)]

        self.assertTrue(rows)

        row = rows[0]

        self.assertEqual(row["gross_commission"], 100)
        self.assertEqual(row["adjustments"], 0)
        self.assertEqual(row["net_commission"], 100)

    def test_commission_by_invoice_script_report(self):
        invoice = self._create_report_invoice_for_sales_person(
            sales_person=self.sales_person,
            posting_date="2026-10-02",
            rate=1000,
            item=self.item,
        )

        columns, data = execute_commission_by_invoice(
            {
                "company": self.company,
                "from_date": "2026-10-02",
                "to_date": "2026-10-02",
            }
        )

        self.assertEqual(
            [column["fieldname"] for column in columns],
            [
                "sales_invoice",
                "gross_commission",
                "adjustments",
                "net_commission",
            ],
        )

        rows = [row for row in data if row["sales_invoice"] == invoice.name]

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["gross_commission"], 100)
        self.assertEqual(rows[0]["adjustments"], 0)
        self.assertEqual(rows[0]["net_commission"], 100)

    def test_commission_by_payee_script_report(self):
        sales_person = self._create_sales_person("E2E Payee Script Report Sales Person")
        payee = self._create_payee(
            "E2E Payee Script Report Payee",
            sales_person,
        )

        invoice = self._create_report_invoice_for_sales_person(
            sales_person=sales_person,
            posting_date="2026-10-02",
            rate=1000,
            item=self.item,
        )

        columns, data = execute_commission_by_payee(
            {
                "company": self.company,
                "from_date": "2026-10-02",
                "to_date": "2026-10-02",
            }
        )

        self.assertEqual(
            [column["fieldname"] for column in columns],
            [
                "commission_payee",
                "gross_commission",
                "adjustments",
                "net_commission",
            ],
        )

        rows = [row for row in data if row["commission_payee"] == payee.name]

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["gross_commission"], 100)
        self.assertEqual(rows[0]["adjustments"], 0)
        self.assertEqual(rows[0]["net_commission"], 100)

    def test_commission_by_plan_script_report(self):
        plan = frappe.get_doc(
            {
                "doctype": "Commission Plan",
                "plan_name": "E2E Plan Script Report Test",
                "company": self.company,
                "currency": self.currency,
                "valid_from": "2026-12-01",
                "status": "Active",
            }
        )
        plan.insert()

        rule = frappe.get_doc(
            {
                "doctype": "Commission Rule",
                "rule_name": "E2E Rule Script Report Plan Test",
                "commission_plan": plan.name,
                "priority": 100,
                "based_on": "Item",
                "item": self.item,
                "calculation_method": "Percentage",
                "rate": 10,
                "enabled": 1,
            }
        )
        rule.insert()

        invoice = self._create_report_invoice_for_sales_person(
            sales_person=self.sales_person,
            posting_date="2026-12-01",
            rate=1000,
            item=self.item,
        )

        columns, data = execute_commission_by_plan(
            {
                "company": self.company,
                "from_date": "2026-12-01",
                "to_date": "2026-12-01",
            }
        )

        self.assertEqual(
            [column["fieldname"] for column in columns],
            [
                "commission_plan",
                "gross_commission",
                "adjustments",
                "net_commission",
            ],
        )

        rows = [row for row in data if row["commission_plan"] == plan.name]

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["gross_commission"], 100)
        self.assertEqual(rows[0]["adjustments"], 0)
        self.assertEqual(rows[0]["net_commission"], 100)

    def test_commission_by_rule_script_report(self):
        plan = frappe.get_doc(
            {
                "doctype": "Commission Plan",
                "plan_name": "E2E Rule Script Report Plan",
                "company": self.company,
                "currency": self.currency,
                "valid_from": "2027-01-01",
                "status": "Active",
            }
        )
        plan.insert()

        rule = frappe.get_doc(
            {
                "doctype": "Commission Rule",
                "rule_name": "E2E Rule Script Report Test",
                "commission_plan": plan.name,
                "priority": 100,
                "based_on": "Item",
                "item": self.item,
                "calculation_method": "Percentage",
                "rate": 10,
                "enabled": 1,
            }
        )
        rule.insert()

        self._create_report_invoice_for_sales_person(
            sales_person=self.sales_person,
            posting_date="2027-01-01",
            rate=1000,
            item=self.item,
        )

        columns, data = execute_commission_by_rule(
            {
                "company": self.company,
                "from_date": "2027-01-01",
                "to_date": "2027-01-01",
            }
        )

        self.assertEqual(
            [column["fieldname"] for column in columns],
            [
                "commission_rule",
                "gross_commission",
                "adjustments",
                "net_commission",
            ],
        )

        rows = [row for row in data if row["commission_rule"] == rule.name]

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["gross_commission"], 100)
        self.assertEqual(rows[0]["adjustments"], 0)
        self.assertEqual(rows[0]["net_commission"], 100)
