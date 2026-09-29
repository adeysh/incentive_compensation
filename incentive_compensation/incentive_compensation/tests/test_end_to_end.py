import frappe

from frappe.tests import IntegrationTestCase
from frappe.utils import getdate

from erpnext.accounts.doctype.sales_invoice.test_sales_invoice import (
    create_sales_invoice,
)

from incentive_compensation.incentive_compensation.commission_engine.payout import (
    create_commission_payout,
)
from incentive_compensation.incentive_compensation.commission_engine.payout_workflow import (
    mark_payout_paid,
    start_payout_processing,
)
from incentive_compensation.incentive_compensation.commission_engine.statement import (
    create_commission_statement,
)
from incentive_compensation.incentive_compensation.commission_engine.statement_workflow import (
    approve_statement,
    post_statement,
    submit_statement_for_review,
    cancel_statement,
)


class TestCommissionEndToEnd(IntegrationTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company = "Incentive Test Company"
        cls.currency = "INR"

        cls.item = cls._create_item("E2E Test Item")

        cls.tiered_item = cls._create_item("E2E Tiered Test Item")

        cls.priority_item = cls._create_item("E2E Priority Test Item")

        cls.no_rule_item = cls._create_item("E2E No Rule Test Item")

        cls.fixed_amount_item = cls._create_item("E2E Fixed Amount Test Item")

        cls.expired_plan_item = cls._create_item("E2E Expired Plan Test Item")

        cls.customer = cls._create_customer()

        cls.sales_person = cls._create_sales_person("E2E Test Sales Person")

        cls.cancellation_sales_person = cls._create_sales_person(
            "E2E Cancellation Sales Person"
        )

        cls.no_payee_sales_person = cls._create_sales_person(
            "E2E No Payee Sales Person"
        )

        cls.cost_center = cls._get_cost_center()
        cls.income_account = cls._get_income_account()
        cls.debit_to = cls._get_receivable_account()

        cls.plan = cls._create_plan()
        cls.newer_plan = cls._create_newer_plan()
        cls.expired_plan = cls._create_expired_plan()
        cls.rule = cls._create_rule()
        cls.newer_plan_rule = cls._create_newer_plan_rule()
        cls.no_payee_rule = cls._create_no_payee_rule()
        cls.fixed_amount_rule = cls._create_fixed_amount_rule()
        cls.expired_plan_rule = cls._create_expired_plan_rule()

        cls.payee = cls._create_payee(
            "E2E Test Commission Payee",
            cls.sales_person,
        )

        cls.cancellation_payee = cls._create_payee(
            "E2E Cancellation Commission Payee",
            cls.cancellation_sales_person,
        )

        cls.allocation_sales_person = cls._create_sales_person(
            "E2E Allocation Sales Person"
        )

        cls.allocation_payee = cls._create_payee(
            "E2E Allocation Commission Payee",
            cls.allocation_sales_person,
        )

        cls.tiered_rule = cls._create_tiered_rule()

        cls.high_priority_rule = cls._create_priority_rule(
            "E2E High Priority Commission Rule",
            priority=50,
            rate=20,
        )

        cls.low_priority_rule = cls._create_priority_rule(
            "E2E Low Priority Commission Rule",
            priority=100,
            rate=10,
        )

    @classmethod
    def _create_item(cls, name):
        if frappe.db.exists("Item", name):
            return name

        item = frappe.get_doc(
            {
                "doctype": "Item",
                "item_code": name,
                "item_name": name,
                "item_group": "All Item Groups",
                "stock_uom": "Nos",
            }
        )

        item.insert()

        return item.name

    @classmethod
    def _create_customer_group(cls):
        name = "E2E Test Customer Group"

        if frappe.db.exists("Customer Group", name):
            return name

        customer_group = frappe.get_doc(
            {
                "doctype": "Customer Group",
                "customer_group_name": name,
                "parent_customer_group": "All Customer Groups",
            }
        )
        customer_group.insert()

        return customer_group.name

    @classmethod
    def _create_customer(cls):
        name = "E2E Test Customer"

        if frappe.db.exists("Customer", name):
            return name

        customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": name,
                "customer_group": cls._create_customer_group(),
                "territory": "All Territories",
            }
        )
        customer.insert()

        return customer.name

    @classmethod
    def _create_sales_person(cls, name):
        if frappe.db.exists("Sales Person", name):
            return name

        sales_person = frappe.get_doc(
            {
                "doctype": "Sales Person",
                "sales_person_name": name,
                "is_group": 0,
                "enabled": 1,
            }
        )
        sales_person.insert()

        return sales_person.name

    @classmethod
    def _get_cost_center(cls):
        cost_center = frappe.db.get_value(
            "Cost Center",
            {
                "company": cls.company,
                "is_group": 0,
            },
            "name",
        )

        if not cost_center:
            frappe.throw(f"No leaf Cost Center found for company '{cls.company}'.")

        return cost_center

    @classmethod
    def _get_income_account(cls):
        account = frappe.db.get_value(
            "Account",
            {
                "company": cls.company,
                "root_type": "Income",
                "is_group": 0,
            },
            "name",
        )

        if not account:
            frappe.throw(f"No leaf Income Account found for company '{cls.company}'.")

        return account

    @classmethod
    def _get_receivable_account(cls):
        account = frappe.db.get_value(
            "Account",
            {
                "company": cls.company,
                "root_type": "Asset",
                "account_type": "Receivable",
                "is_group": 0,
            },
            "name",
        )

        if not account:
            frappe.throw(
                f"No leaf Receivable Account found for company '{cls.company}'."
            )

        return account

    @classmethod
    def _create_plan(cls):
        name = "E2E Test Commission Plan"

        if frappe.db.exists("Commission Plan", {"plan_name": name}):
            return frappe.get_doc(
                "Commission Plan",
                {"plan_name": name},
            )

        plan = frappe.get_doc(
            {
                "doctype": "Commission Plan",
                "plan_name": name,
                "company": cls.company,
                "currency": cls.currency,
                "valid_from": "2026-01-01",
                "status": "Active",
            }
        )
        plan.insert()

        return plan

    @classmethod
    def _create_newer_plan(cls):
        name = "E2E Newer Commission Plan"

        existing = frappe.db.exists(
            "Commission Plan",
            {"plan_name": name},
        )

        if existing:
            plan = frappe.get_doc(
                "Commission Plan",
                existing,
            )

            plan.company = cls.company
            plan.currency = cls.currency
            plan.valid_from = "2026-10-03"
            plan.valid_to = None
            plan.status = "Active"

            plan.save()

            return plan

        plan = frappe.get_doc(
            {
                "doctype": "Commission Plan",
                "plan_name": name,
                "company": cls.company,
                "currency": cls.currency,
                "valid_from": "2026-10-03",
                "status": "Active",
            }
        )

        plan.insert()

        return plan

    @classmethod
    def _create_expired_plan(cls):
        name = "E2E Expired Commission Plan"

        existing = frappe.db.exists(
            "Commission Plan",
            {"plan_name": name},
        )

        if existing:
            plan = frappe.get_doc("Commission Plan", existing)

            plan.company = cls.company
            plan.currency = cls.currency
            plan.valid_from = "2026-01-01"
            plan.valid_to = "2026-09-15"
            plan.status = "Active"

            plan.save()
            return plan

        plan = frappe.get_doc(
            {
                "doctype": "Commission Plan",
                "plan_name": name,
                "company": cls.company,
                "currency": cls.currency,
                "valid_from": "2026-01-01",
                "valid_to": "2026-09-15",
                "status": "Active",
            }
        )

        plan.insert()
        return plan

    @classmethod
    def _create_rule(cls):
        name = "E2E Test Commission Rule"

        if frappe.db.exists("Commission Rule", {"rule_name": name}):
            return frappe.get_doc(
                "Commission Rule",
                {"rule_name": name},
            )

        rule = frappe.get_doc(
            {
                "doctype": "Commission Rule",
                "rule_name": name,
                "commission_plan": cls.plan.name,
                "priority": 100,
                "based_on": "Item",
                "item": cls.item,
                "calculation_method": "Percentage",
                "rate": 10,
                "enabled": 1,
            }
        )
        rule.insert()

        return rule

    @classmethod
    def _create_newer_plan_rule(cls):
        name = "E2E Newer Plan Commission Rule"

        existing = frappe.db.exists(
            "Commission Rule",
            {"rule_name": name},
        )

        if existing:
            rule = frappe.get_doc(
                "Commission Rule",
                existing,
            )

            rule.commission_plan = cls.newer_plan.name
            rule.priority = 100
            rule.based_on = "Item"
            rule.item = cls.priority_item
            rule.calculation_method = "Percentage"
            rule.rate = 20
            rule.enabled = 1

            rule.save()

            return rule

        rule = frappe.get_doc(
            {
                "doctype": "Commission Rule",
                "rule_name": name,
                "commission_plan": cls.newer_plan.name,
                "priority": 100,
                "based_on": "Item",
                "item": cls.priority_item,
                "calculation_method": "Percentage",
                "rate": 20,
                "enabled": 1,
            }
        )

        rule.insert()

        return rule

    @classmethod
    def _create_tiered_rule(cls):
        name = "E2E Tiered Commission Rule"

        existing = frappe.db.exists(
            "Commission Rule",
            {"rule_name": name},
        )

        if existing:
            rule = frappe.get_doc(
                "Commission Rule",
                existing,
            )

            rule.item = cls.tiered_item
            rule.based_on = "Item"
            rule.calculation_method = "Tiered"
            rule.priority = 50
            rule.enabled = 1

            rule.save()

            return rule

        rule = frappe.get_doc(
            {
                "doctype": "Commission Rule",
                "rule_name": name,
                "commission_plan": cls.plan.name,
                "priority": 50,
                "based_on": "Item",
                "item": cls.tiered_item,
                "calculation_method": "Tiered",
                "enabled": 1,
            }
        )

        rule.append(
            "tiers",
            {
                "from_amount": 0,
                "to_amount": 5000,
                "rate": 5,
                "description": "First ₹5,000",
            },
        )

        rule.append(
            "tiers",
            {
                "from_amount": 5000,
                "to_amount": 10000,
                "rate": 10,
                "description": "₹5,000 to ₹10,000",
            },
        )

        rule.append(
            "tiers",
            {
                "from_amount": 10000,
                "rate": 15,
                "description": "Above ₹10,000",
            },
        )

        rule.insert()

        return rule

    @classmethod
    def _create_expired_plan_rule(cls):
        name = "E2E Expired Plan Commission Rule"

        existing = frappe.db.exists(
            "Commission Rule",
            {"rule_name": name},
        )

        if existing:
            rule = frappe.get_doc("Commission Rule", existing)

            rule.commission_plan = cls.expired_plan.name
            rule.priority = 100
            rule.based_on = "Item"
            rule.item = cls.expired_plan_item
            rule.calculation_method = "Percentage"
            rule.rate = 10
            rule.enabled = 1

            rule.save()
            return rule

        rule = frappe.get_doc(
            {
                "doctype": "Commission Rule",
                "rule_name": name,
                "commission_plan": cls.expired_plan.name,
                "priority": 100,
                "based_on": "Item",
                "item": cls.expired_plan_item,
                "calculation_method": "Percentage",
                "rate": 10,
                "enabled": 1,
            }
        )

        rule.insert()
        return rule

    @classmethod
    def _create_payee(cls, name, sales_person):
        if frappe.db.exists(
            "Commission Payee",
            {"payee_name": name},
        ):
            return frappe.get_doc(
                "Commission Payee",
                {"payee_name": name},
            )

        payee = frappe.get_doc(
            {
                "doctype": "Commission Payee",
                "payee_name": name,
                "payee_type": "Employee",
                "sales_person": sales_person,
                "enabled": 1,
            }
        )

        payee.insert()

        return payee

    @classmethod
    def _create_priority_rule(cls, name, priority, rate):
        existing = frappe.db.exists(
            "Commission Rule",
            {"rule_name": name},
        )

        if existing:
            rule = frappe.get_doc("Commission Rule", existing)

            rule.commission_plan = cls.plan.name
            rule.priority = priority
            rule.based_on = "Item"
            rule.item = cls.priority_item
            rule.calculation_method = "Percentage"
            rule.rate = rate
            rule.enabled = 1

            rule.save()

            return rule

        rule = frappe.get_doc(
            {
                "doctype": "Commission Rule",
                "rule_name": name,
                "commission_plan": cls.plan.name,
                "priority": priority,
                "based_on": "Item",
                "item": cls.priority_item,
                "calculation_method": "Percentage",
                "rate": rate,
                "enabled": 1,
            }
        )

        rule.insert()

        return rule

    @classmethod
    def _create_no_payee_rule(cls):
        name = "E2E No Payee Commission Rule"

        existing = frappe.db.exists(
            "Commission Rule",
            {"rule_name": name},
        )

        if existing:
            rule = frappe.get_doc("Commission Rule", existing)

            rule.commission_plan = cls.plan.name
            rule.priority = 100
            rule.based_on = "Sales Person"
            rule.sales_person = cls.no_payee_sales_person
            rule.calculation_method = "Percentage"
            rule.rate = 10
            rule.enabled = 1

            rule.save()
            return rule

        rule = frappe.get_doc(
            {
                "doctype": "Commission Rule",
                "rule_name": name,
                "commission_plan": cls.plan.name,
                "priority": 100,
                "based_on": "Sales Person",
                "sales_person": cls.no_payee_sales_person,
                "calculation_method": "Percentage",
                "rate": 10,
                "enabled": 1,
            }
        )

        rule.insert()
        return rule

    @classmethod
    def _create_fixed_amount_rule(cls):
        name = "E2E Fixed Amount Commission Rule"

        existing = frappe.db.exists(
            "Commission Rule",
            {"rule_name": name},
        )

        if existing:
            rule = frappe.get_doc("Commission Rule", existing)

            rule.commission_plan = cls.plan.name
            rule.priority = 100
            rule.based_on = "Item"
            rule.item = cls.fixed_amount_item
            rule.calculation_method = "Fixed Amount"
            rule.fixed_amount = 250
            rule.rate = None
            rule.enabled = 1

            rule.save()
            return rule

        rule = frappe.get_doc(
            {
                "doctype": "Commission Rule",
                "rule_name": name,
                "commission_plan": cls.plan.name,
                "priority": 100,
                "based_on": "Item",
                "item": cls.fixed_amount_item,
                "calculation_method": "Fixed Amount",
                "fixed_amount": 250,
                "enabled": 1,
            }
        )

        rule.insert()
        return rule

    def test_sales_invoice_to_paid_commission(self):
        invoice = create_sales_invoice(
            company=self.company,
            customer=self.customer,
            debit_to=self.debit_to,
            item=self.item,
            qty=1,
            rate=1000,
            currency=self.currency,
            posting_date="2026-09-28",
            parent_cost_center=self.cost_center,
            cost_center=self.cost_center,
            income_account=self.income_account,
            do_not_submit=True,
        )

        invoice.append(
            "sales_team",
            {
                "sales_person": self.sales_person,
                "allocated_percentage": 100,
            },
        )

        invoice.submit()

        ledger_entries = frappe.get_all(
            "Commission Ledger",
            filters={
                "sales_invoice": invoice.name,
            },
            fields=[
                "name",
                "commission_amount",
                "commission_payee",
                "commission_rule",
                "commission_plan",
                "status",
            ],
        )

        self.assertEqual(len(ledger_entries), 1)

        ledger = ledger_entries[0]

        self.assertEqual(
            ledger.commission_payee,
            self.payee.name,
        )

        self.assertEqual(
            ledger.commission_rule,
            self.rule.name,
        )

        self.assertEqual(
            ledger.commission_plan,
            self.plan.name,
        )

        self.assertEqual(
            ledger.commission_amount,
            100,
        )

        self.assertEqual(
            ledger.status,
            "Calculated",
        )

        statement = create_commission_statement(
            commission_payee=self.payee.name,
            company=self.company,
            currency=self.currency,
            from_date=invoice.posting_date,
            to_date=invoice.posting_date,
        )

        self.assertEqual(
            statement.status,
            "Generated",
        )

        self.assertEqual(
            statement.gross_commission,
            100,
        )

        self.assertEqual(
            statement.adjustments,
            0,
        )

        self.assertEqual(
            statement.net_commission,
            100,
        )

        self.assertEqual(
            len(statement.ledger_entries),
            1,
        )

        self.assertEqual(
            statement.ledger_entries[0].commission_ledger,
            ledger.name,
        )

        submit_statement_for_review(statement.name)

        statement.reload()

        self.assertEqual(
            statement.status,
            "Under Review",
        )

        approve_statement(statement.name)

        statement.reload()

        self.assertEqual(
            statement.status,
            "Approved",
        )

        post_statement(statement.name)

        statement.reload()

        self.assertEqual(
            statement.status,
            "Posted",
        )

        payout = create_commission_payout(statement)

        self.assertEqual(
            payout.status,
            "Pending",
        )

        self.assertEqual(
            payout.amount,
            100,
        )

        start_payout_processing(payout.name)

        payout.reload()

        self.assertEqual(
            payout.status,
            "Processing",
        )

        payout.payment_date = invoice.posting_date
        payout.payment_reference = "E2E-TEST-PAY-001"
        payout.save()

        mark_payout_paid(payout.name)

        payout.reload()
        statement.reload()

        self.assertEqual(
            payout.status,
            "Paid",
        )

        self.assertEqual(
            payout.payment_date,
            getdate(invoice.posting_date),
        )

        self.assertEqual(
            payout.payment_reference,
            "E2E-TEST-PAY-001",
        )

        self.assertEqual(
            statement.status,
            "Paid",
        )

    def test_sales_invoice_cancellation_reverses_commission(self):
        invoice = create_sales_invoice(
            company=self.company,
            customer=self.customer,
            debit_to=self.debit_to,
            item=self.item,
            qty=1,
            rate=1000,
            currency=self.currency,
            posting_date="2026-09-27",
            parent_cost_center=self.cost_center,
            cost_center=self.cost_center,
            income_account=self.income_account,
            do_not_submit=True,
        )

        invoice.append(
            "sales_team",
            {
                "sales_person": self.cancellation_sales_person,
                "allocated_percentage": 100,
            },
        )

        invoice.submit()

        ledger_entries = frappe.get_all(
            "Commission Ledger",
            filters={
                "sales_invoice": invoice.name,
            },
            fields=[
                "name",
                "commission_amount",
                "status",
                "entry_type",
                "reversal_of",
            ],
            order_by="creation asc",
        )

        self.assertEqual(len(ledger_entries), 1)

        original_ledger = ledger_entries[0]

        self.assertEqual(
            original_ledger.commission_amount,
            100,
        )
        self.assertEqual(
            original_ledger.entry_type,
            "Commission",
        )
        self.assertEqual(
            original_ledger.status,
            "Calculated",
        )

        invoice.cancel()

        ledger_entries = frappe.get_all(
            "Commission Ledger",
            filters={
                "sales_invoice": invoice.name,
            },
            fields=[
                "name",
                "commission_amount",
                "status",
                "entry_type",
                "reversal_of",
            ],
            order_by="creation asc",
        )

        self.assertEqual(len(ledger_entries), 2)

        original_ledger = ledger_entries[0]
        reversal_ledger = ledger_entries[1]

        self.assertEqual(
            original_ledger.entry_type,
            "Commission",
        )
        self.assertEqual(
            original_ledger.status,
            "Reversed",
        )

        self.assertEqual(
            reversal_ledger.entry_type,
            "Reversal",
        )
        self.assertEqual(
            reversal_ledger.commission_amount,
            -100,
        )
        self.assertEqual(
            reversal_ledger.reversal_of,
            original_ledger.name,
        )
        self.assertEqual(
            reversal_ledger.status,
            "Calculated",
        )

    def test_commission_ledger_creation_is_idempotent(self):
        invoice = create_sales_invoice(
            company=self.company,
            customer=self.customer,
            debit_to=self.debit_to,
            item=self.item,
            qty=1,
            rate=1000,
            currency=self.currency,
            posting_date="2026-09-29",
            parent_cost_center=self.cost_center,
            cost_center=self.cost_center,
            income_account=self.income_account,
            do_not_submit=True,
        )

        invoice.append(
            "sales_team",
            {
                "sales_person": self.sales_person,
                "allocated_percentage": 100,
            },
        )

        invoice.submit()

        ledger_entries = frappe.get_all(
            "Commission Ledger",
            filters={
                "sales_invoice": invoice.name,
            },
            fields=[
                "name",
                "commission_amount",
                "source_key",
            ],
        )

        self.assertEqual(len(ledger_entries), 1)

        original_ledger = ledger_entries[0]

        self.assertEqual(
            original_ledger.commission_amount,
            100,
        )

        # Simulate the same commission-processing operation
        # happening again for the same invoice.
        from incentive_compensation.incentive_compensation.commission_engine.ledger import (
            create_ledger_entries_for_invoice,
        )

        returned_ledgers = create_ledger_entries_for_invoice(invoice)

        self.assertEqual(len(returned_ledgers), 1)

        self.assertEqual(
            returned_ledgers[0].name,
            original_ledger.name,
        )

        ledger_entries = frappe.get_all(
            "Commission Ledger",
            filters={
                "sales_invoice": invoice.name,
            },
            fields=[
                "name",
                "commission_amount",
                "source_key",
            ],
        )

        self.assertEqual(len(ledger_entries), 1)

        self.assertEqual(
            ledger_entries[0].name,
            original_ledger.name,
        )

        self.assertEqual(
            ledger_entries[0].commission_amount,
            100,
        )

    def test_sales_team_allocation_splits_commission(self):
        invoice = create_sales_invoice(
            company=self.company,
            customer=self.customer,
            debit_to=self.debit_to,
            item=self.item,
            qty=1,
            rate=10000,
            currency=self.currency,
            posting_date="2026-09-30",
            parent_cost_center=self.cost_center,
            cost_center=self.cost_center,
            income_account=self.income_account,
            do_not_submit=True,
        )

        invoice.append(
            "sales_team",
            {
                "sales_person": self.sales_person,
                "allocated_percentage": 60,
            },
        )

        invoice.append(
            "sales_team",
            {
                "sales_person": self.allocation_sales_person,
                "allocated_percentage": 40,
            },
        )

        invoice.submit()

        ledger_entries = frappe.get_all(
            "Commission Ledger",
            filters={
                "sales_invoice": invoice.name,
            },
            fields=[
                "name",
                "commission_amount",
                "base_amount",
                "commission_payee",
                "commission_rule",
                "status",
            ],
            order_by="creation asc",
        )

        self.assertEqual(len(ledger_entries), 2)

        first_ledger = ledger_entries[0]
        second_ledger = ledger_entries[1]

        self.assertEqual(
            first_ledger.commission_amount,
            600,
        )

        self.assertEqual(
            first_ledger.base_amount,
            6000,
        )

        self.assertEqual(
            first_ledger.commission_payee,
            self.payee.name,
        )

        self.assertEqual(
            second_ledger.commission_amount,
            400,
        )

        self.assertEqual(
            second_ledger.base_amount,
            4000,
        )

        self.assertEqual(
            second_ledger.commission_payee,
            self.allocation_payee.name,
        )

        self.assertEqual(
            first_ledger.commission_rule,
            self.rule.name,
        )

        self.assertEqual(
            second_ledger.commission_rule,
            self.rule.name,
        )

        self.assertEqual(
            first_ledger.status,
            "Calculated",
        )

        self.assertEqual(
            second_ledger.status,
            "Calculated",
        )

        total_commission = sum(entry.commission_amount for entry in ledger_entries)

        self.assertEqual(
            total_commission,
            1000,
        )

    def test_tiered_commission_is_calculated_end_to_end(self):
        invoice = create_sales_invoice(
            company=self.company,
            customer=self.customer,
            debit_to=self.debit_to,
            item=self.tiered_item,
            qty=1,
            rate=12000,
            currency=self.currency,
            posting_date="2026-10-01",
            parent_cost_center=self.cost_center,
            cost_center=self.cost_center,
            income_account=self.income_account,
            do_not_submit=True,
        )

        invoice.append(
            "sales_team",
            {
                "sales_person": self.sales_person,
                "allocated_percentage": 100,
            },
        )

        invoice.submit()

        ledger_entries = frappe.get_all(
            "Commission Ledger",
            filters={
                "sales_invoice": invoice.name,
            },
            fields=[
                "name",
                "commission_amount",
                "base_amount",
                "commission_rule",
                "calculation_method",
                "commission_payee",
                "status",
            ],
        )

        self.assertEqual(len(ledger_entries), 1)

        ledger = ledger_entries[0]

        self.assertEqual(
            ledger.commission_rule,
            self.tiered_rule.name,
        )

        self.assertEqual(
            ledger.calculation_method,
            "Tiered",
        )

        self.assertEqual(
            ledger.base_amount,
            12000,
        )

        self.assertEqual(
            ledger.commission_amount,
            1050,
        )

        self.assertEqual(
            ledger.commission_payee,
            self.payee.name,
        )

        self.assertEqual(
            ledger.status,
            "Calculated",
        )

    def test_fixed_amount_commission_is_calculated_end_to_end(self):
        invoice = create_sales_invoice(
            company=self.company,
            customer=self.customer,
            debit_to=self.debit_to,
            item=self.fixed_amount_item,
            qty=1,
            rate=10000,
            currency=self.currency,
            posting_date="2026-10-01",
            parent_cost_center=self.cost_center,
            cost_center=self.cost_center,
            income_account=self.income_account,
            do_not_submit=True,
        )

        invoice.append(
            "sales_team",
            {
                "sales_person": self.sales_person,
                "allocated_percentage": 100,
            },
        )

        invoice.submit()

        ledger_entries = frappe.get_all(
            "Commission Ledger",
            filters={
                "sales_invoice": invoice.name,
            },
            fields=[
                "name",
                "commission_amount",
                "base_amount",
                "fixed_amount",
                "commission_rule",
                "calculation_method",
                "commission_payee",
                "status",
            ],
        )

        self.assertEqual(len(ledger_entries), 1)

        ledger = ledger_entries[0]

        self.assertEqual(
            ledger.commission_rule,
            self.fixed_amount_rule.name,
        )

        self.assertEqual(
            ledger.calculation_method,
            "Fixed Amount",
        )

        self.assertEqual(
            ledger.base_amount,
            10000,
        )

        self.assertEqual(
            ledger.fixed_amount,
            250,
        )

        self.assertEqual(
            ledger.commission_amount,
            250,
        )

        self.assertEqual(
            ledger.commission_payee,
            self.payee.name,
        )

        self.assertEqual(
            ledger.status,
            "Calculated",
        )

    def test_rule_priority_selects_highest_priority_rule(self):
        invoice = create_sales_invoice(
            company=self.company,
            customer=self.customer,
            debit_to=self.debit_to,
            item=self.priority_item,
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
                "sales_person": self.sales_person,
                "allocated_percentage": 100,
            },
        )

        invoice.submit()

        ledger_entries = frappe.get_all(
            "Commission Ledger",
            filters={
                "sales_invoice": invoice.name,
            },
            fields=[
                "name",
                "commission_amount",
                "commission_rule",
                "rate",
                "status",
            ],
        )

        self.assertEqual(len(ledger_entries), 1)

        ledger = ledger_entries[0]

        self.assertEqual(
            ledger.commission_rule,
            self.high_priority_rule.name,
        )

        self.assertEqual(
            ledger.rate,
            20,
        )

        self.assertEqual(
            ledger.commission_amount,
            200,
        )

        self.assertEqual(
            ledger.status,
            "Calculated",
        )

    def test_newest_active_plan_is_selected(self):
        invoice = create_sales_invoice(
            company=self.company,
            customer=self.customer,
            debit_to=self.debit_to,
            item=self.priority_item,
            qty=1,
            rate=1000,
            currency=self.currency,
            posting_date="2026-10-03",
            parent_cost_center=self.cost_center,
            cost_center=self.cost_center,
            income_account=self.income_account,
            do_not_submit=True,
        )

        invoice.append(
            "sales_team",
            {
                "sales_person": self.sales_person,
                "allocated_percentage": 100,
            },
        )

        invoice.submit()

        ledger_entries = frappe.get_all(
            "Commission Ledger",
            filters={
                "sales_invoice": invoice.name,
            },
            fields=[
                "name",
                "commission_amount",
                "commission_plan",
                "commission_rule",
                "status",
            ],
        )

        self.assertEqual(len(ledger_entries), 1)

        ledger = ledger_entries[0]

        self.assertEqual(
            ledger.commission_plan,
            self.newer_plan.name,
        )

        self.assertEqual(
            ledger.commission_rule,
            self.newer_plan_rule.name,
        )

        self.assertEqual(
            ledger.commission_amount,
            200,
        )

        self.assertEqual(
            ledger.status,
            "Calculated",
        )

    def test_sales_invoice_with_no_matching_rule_creates_no_commission(self):
        invoice = create_sales_invoice(
            company=self.company,
            customer=self.customer,
            debit_to=self.debit_to,
            item=self.no_rule_item,
            qty=1,
            rate=1000,
            currency=self.currency,
            posting_date="2026-09-28",
            parent_cost_center=self.cost_center,
            cost_center=self.cost_center,
            income_account=self.income_account,
            do_not_submit=True,
        )

        invoice.append(
            "sales_team",
            {
                "sales_person": self.sales_person,
                "allocated_percentage": 100,
            },
        )

        invoice.submit()

        ledger_entries = frappe.get_all(
            "Commission Ledger",
            filters={
                "sales_invoice": invoice.name,
            },
            fields=["name"],
        )

        self.assertEqual(ledger_entries, [])

    def test_sales_invoice_with_missing_commission_payee_fails(self):
        invoice = create_sales_invoice(
            company=self.company,
            customer=self.customer,
            debit_to=self.debit_to,
            item=self.item,
            qty=1,
            rate=1000,
            currency=self.currency,
            posting_date="2026-09-28",
            parent_cost_center=self.cost_center,
            cost_center=self.cost_center,
            income_account=self.income_account,
            do_not_submit=True,
        )

        invoice.append(
            "sales_team",
            {
                "sales_person": self.no_payee_sales_person,
                "allocated_percentage": 100,
            },
        )

        with self.assertRaises(frappe.ValidationError) as context:
            invoice.submit()

        self.assertEqual(
            str(context.exception),
            (
                "No active Commission Payee found for Sales Person "
                '"E2E No Payee Sales Person".'
            ),
        )

    def test_sales_invoice_with_expired_plan_creates_no_commission(self):
        invoice = create_sales_invoice(
            company=self.company,
            customer=self.customer,
            debit_to=self.debit_to,
            item=self.expired_plan_item,
            qty=1,
            rate=1000,
            currency=self.currency,
            posting_date="2026-09-28",
            parent_cost_center=self.cost_center,
            cost_center=self.cost_center,
            income_account=self.income_account,
            do_not_submit=True,
        )

        invoice.append(
            "sales_team",
            {
                "sales_person": self.sales_person,
                "allocated_percentage": 100,
            },
        )

        invoice.submit()

        ledger_entries = frappe.get_all(
            "Commission Ledger",
            filters={
                "sales_invoice": invoice.name,
            },
            fields=["name"],
        )

        self.assertEqual(ledger_entries, [])

    def test_statement_does_not_include_already_stated_ledger(self):
        invoice = create_sales_invoice(
            company=self.company,
            customer=self.customer,
            debit_to=self.debit_to,
            item=self.priority_item,
            qty=1,
            rate=1000,
            currency=self.currency,
            posting_date="2026-10-04",
            parent_cost_center=self.cost_center,
            cost_center=self.cost_center,
            income_account=self.income_account,
            do_not_submit=True,
        )

        invoice.append(
            "sales_team",
            {
                "sales_person": self.sales_person,
                "allocated_percentage": 100,
            },
        )

        invoice.submit()

        first_statement = create_commission_statement(
            commission_payee=self.payee.name,
            company=self.company,
            currency=self.currency,
            from_date=invoice.posting_date,
            to_date=invoice.posting_date,
        )

        self.assertEqual(
            len(first_statement.ledger_entries),
            1,
        )

        self.assertEqual(
            first_statement.ledger_entries[0].sales_invoice,
            invoice.name,
        )

        with self.assertRaises(frappe.ValidationError):
            create_commission_statement(
                commission_payee=self.payee.name,
                company=self.company,
                currency=self.currency,
                from_date=invoice.posting_date,
                to_date=invoice.posting_date,
            )

    def test_cancelled_statement_allows_ledger_to_be_stated_again(self):
        invoice = create_sales_invoice(
            company=self.company,
            customer=self.customer,
            debit_to=self.debit_to,
            item=self.priority_item,
            qty=1,
            rate=1000,
            currency=self.currency,
            posting_date="2026-10-05",
            parent_cost_center=self.cost_center,
            cost_center=self.cost_center,
            income_account=self.income_account,
            do_not_submit=True,
        )

        invoice.append(
            "sales_team",
            {
                "sales_person": self.sales_person,
                "allocated_percentage": 100,
            },
        )

        invoice.submit()

        first_statement = create_commission_statement(
            commission_payee=self.payee.name,
            company=self.company,
            currency=self.currency,
            from_date=invoice.posting_date,
            to_date=invoice.posting_date,
        )

        self.assertEqual(
            len(first_statement.ledger_entries),
            1,
        )

        ledger_name = first_statement.ledger_entries[0].commission_ledger

        submit_statement_for_review(first_statement.name)

        first_statement.reload()
        self.assertEqual(first_statement.status, "Under Review")

        cancel_statement(first_statement.name)

        first_statement.reload()
        self.assertEqual(first_statement.status, "Cancelled")

        second_statement = create_commission_statement(
            commission_payee=self.payee.name,
            company=self.company,
            currency=self.currency,
            from_date=invoice.posting_date,
            to_date=invoice.posting_date,
        )

        self.assertEqual(
            len(second_statement.ledger_entries),
            1,
        )

        self.assertEqual(
            second_statement.ledger_entries[0].commission_ledger,
            ledger_name,
        )
