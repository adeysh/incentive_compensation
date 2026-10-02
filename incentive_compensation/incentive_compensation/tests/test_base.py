import frappe

from frappe.tests import IntegrationTestCase


class CommissionTestCase(IntegrationTestCase):

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

