import frappe

from frappe.tests import IntegrationTestCase


from incentive_compensation.incentive_compensation.commission_engine.resolver import (
    get_active_plans,
    get_applicable_plan,
    get_matching_rules,
    get_rule_tiers,
    get_commission_payee,
)


class TestResolver(IntegrationTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company = "Incentive Test Company"
        cls.currency = "INR"

        cls.item = cls._create_item()
        cls.item_group = cls._create_item_group()
        cls.customer = cls._create_customer()
        cls.customer_group = cls._create_customer_group()
        cls.territory = cls._create_territory()
        cls.sales_person = cls._create_sales_person()

    @classmethod
    def _create_item_group(cls):
        name = "Resolver Test Item Group"

        if frappe.db.exists("Item Group", name):
            return name

        item_group = frappe.get_doc(
            {
                "doctype": "Item Group",
                "item_group_name": name,
                "parent_item_group": "All Item Groups",
            }
        )
        item_group.insert()

        return item_group.name

    @classmethod
    def _create_item(cls):
        name = "Resolver Test Item"

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
        name = "Resolver Test Customer Group"

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
        name = "Resolver Test Customer"

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
    def _create_territory(cls):
        name = "Resolver Test Territory"

        if frappe.db.exists("Territory", name):
            return name

        territory = frappe.get_doc(
            {
                "doctype": "Territory",
                "territory_name": name,
                "parent_territory": "All Territories",
            }
        )
        territory.insert()

        return territory.name

    @classmethod
    def _create_sales_person(cls, name="Resolver Test Sales Person"):
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
    def _create_company(cls, name):
        if frappe.db.exists("Company", name):
            return name

        company = frappe.get_doc(
            {
                "doctype": "Company",
                "company_name": name,
                "abbr": "RNPC",
                "default_currency": cls.currency,
                "country": "India",
            }
        )
        company.insert()

        return company.name

    def create_plan(
        self,
        plan_name,
        valid_from,
        valid_to=None,
        status="Active",
        company=None,
    ):
        plan = frappe.get_doc(
            {
                "doctype": "Commission Plan",
                "plan_name": plan_name,
                "company": company or self.company,
                "currency": self.currency,
                "valid_from": valid_from,
                "valid_to": valid_to,
                "status": status,
            }
        )

        plan.insert()
        return plan

    def create_rule(
        self,
        rule_name,
        plan,
        based_on,
        priority=100,
        enabled=1,
        **kwargs,
    ):
        rule = frappe.get_doc(
            {
                "doctype": "Commission Rule",
                "rule_name": rule_name,
                "commission_plan": plan.name,
                "priority": priority,
                "based_on": based_on,
                "enabled": enabled,
                "calculation_method": "Percentage",
                "rate": 10,
                **kwargs,
            }
        )

        rule.insert()
        return rule

    def test_active_plan_is_returned(self):
        plan = self.create_plan(
            "Resolver Active Plan",
            "2026-01-01",
        )

        plans = get_active_plans(
            self.company,
            "2026-06-01",
        )

        names = [plan.name for plan in plans]

        self.assertIn(plan.name, names)

    def test_future_plan_is_not_active(self):
        plan = self.create_plan(
            "Resolver Future Plan",
            "2026-07-01",
        )

        plans = get_active_plans(
            self.company,
            "2026-06-01",
        )

        names = [plan.name for plan in plans]

        self.assertNotIn(plan.name, names)

    def test_expired_plan_is_not_active(self):
        plan = self.create_plan(
            "Resolver Expired Plan",
            "2026-01-01",
            valid_to="2026-05-31",
        )

        plans = get_active_plans(
            self.company,
            "2026-06-01",
        )

        names = [plan.name for plan in plans]

        self.assertNotIn(plan.name, names)

    def test_disabled_plan_is_not_active(self):
        plan = self.create_plan(
            "Resolver Disabled Plan",
            "2026-01-01",
            status="Disabled",
        )

        plans = get_active_plans(
            self.company,
            "2026-06-01",
        )

        names = [plan.name for plan in plans]

        self.assertNotIn(plan.name, names)

    def test_newest_valid_plan_is_selected(self):
        older_plan = self.create_plan(
            "Resolver Older Plan",
            "2026-01-01",
        )

        newer_plan = self.create_plan(
            "Resolver Newer Plan",
            "2026-05-01",
        )

        selected_plan = get_applicable_plan(
            self.company,
            "2026-06-01",
        )

        self.assertEqual(
            selected_plan.name,
            newer_plan.name,
        )

        self.assertNotEqual(
            selected_plan.name,
            older_plan.name,
        )

    def test_no_valid_plan_returns_none(self):
        company = self._create_company("Resolver No Plan Company")

        self.create_plan(
            "Resolver Future Only Plan",
            "2027-01-01",
            company=company,
        )

        selected_plan = get_applicable_plan(
            company,
            "2026-06-01",
        )

        self.assertIsNone(selected_plan)

    def test_item_rule_matches(self):
        plan = self.create_plan(
            "Resolver Item Rule Plan",
            "2026-01-01",
        )

        rule = self.create_rule(
            "Resolver Item Rule",
            plan,
            based_on="Item",
            item=self.item,
        )

        transaction = {
            "item": self.item,
        }

        matches = get_matching_rules(
            transaction,
            plan,
        )

        self.assertIn(
            rule.name,
            [match.name for match in matches],
        )

    def test_item_rule_does_not_match_different_item(self):
        plan = self.create_plan(
            "Resolver Item Mismatch Plan",
            "2026-01-01",
        )

        rule = self.create_rule(
            "Resolver Item Mismatch Rule",
            plan,
            based_on="Item",
            item=self.item,
        )

        transaction = {
            "item": "Different Item",
        }

        matches = get_matching_rules(
            transaction,
            plan,
        )

        self.assertNotIn(
            rule.name,
            [match.name for match in matches],
        )

    def test_item_group_rule_matches(self):
        plan = self.create_plan(
            "Resolver Item Group Plan",
            "2026-01-01",
        )

        rule = self.create_rule(
            "Resolver Item Group Rule",
            plan,
            based_on="Item Group",
            item_group=self.item_group,
        )

        transaction = {
            "item_group": self.item_group,
        }

        matches = get_matching_rules(
            transaction,
            plan,
        )

        self.assertIn(
            rule.name,
            [match.name for match in matches],
        )

    def test_sales_person_rule_matches(self):
        plan = self.create_plan(
            "Resolver Sales Person Plan",
            "2026-01-01",
        )

        rule = self.create_rule(
            "Resolver Sales Person Rule",
            plan,
            based_on="Sales Person",
            sales_person=self.sales_person,
        )

        transaction = {
            "sales_person": self.sales_person,
        }

        matches = get_matching_rules(
            transaction,
            plan,
        )

        self.assertIn(
            rule.name,
            [match.name for match in matches],
        )

    def test_customer_rule_matches(self):
        plan = self.create_plan(
            "Resolver Customer Plan",
            "2026-01-01",
        )

        rule = self.create_rule(
            "Resolver Customer Rule",
            plan,
            based_on="Customer",
            customer=self.customer,
        )

        transaction = {
            "customer": self.customer,
        }

        matches = get_matching_rules(
            transaction,
            plan,
        )

        self.assertIn(
            rule.name,
            [match.name for match in matches],
        )

    def test_customer_group_rule_matches(self):
        plan = self.create_plan(
            "Resolver Customer Group Plan",
            "2026-01-01",
        )

        rule = self.create_rule(
            "Resolver Customer Group Rule",
            plan,
            based_on="Customer Group",
            customer_group=self.customer_group,
        )

        transaction = {
            "customer_group": self.customer_group,
        }

        matches = get_matching_rules(
            transaction,
            plan,
        )

        self.assertIn(
            rule.name,
            [match.name for match in matches],
        )

    def test_territory_rule_matches(self):
        plan = self.create_plan(
            "Resolver Territory Plan",
            "2026-01-01",
        )

        rule = self.create_rule(
            "Resolver Territory Rule",
            plan,
            based_on="Territory",
            territory=self.territory,
        )

        transaction = {
            "territory": self.territory,
        }

        matches = get_matching_rules(
            transaction,
            plan,
        )

        self.assertIn(
            rule.name,
            [match.name for match in matches],
        )

    def test_rule_from_different_plan_is_ignored(self):
        selected_plan = self.create_plan(
            "Resolver Selected Plan",
            "2026-01-01",
        )

        other_plan = self.create_plan(
            "Resolver Other Plan",
            "2026-01-01",
        )

        other_rule = self.create_rule(
            "Resolver Other Plan Rule",
            other_plan,
            based_on="Item",
            item=self.item,
        )

        transaction = {
            "item": self.item,
        }

        matches = get_matching_rules(
            transaction,
            selected_plan,
        )

        self.assertNotIn(
            other_rule.name,
            [match.name for match in matches],
        )

    def test_disabled_rule_is_ignored(self):
        plan = self.create_plan(
            "Resolver Disabled Rule Plan",
            "2026-01-01",
        )

        rule = self.create_rule(
            "Resolver Disabled Rule",
            plan,
            based_on="Item",
            item=self.item,
            enabled=0,
        )

        transaction = {
            "item": self.item,
        }

        matches = get_matching_rules(
            transaction,
            plan,
        )

        self.assertNotIn(
            rule.name,
            [match.name for match in matches],
        )

    def test_lower_priority_rule_comes_first(self):
        plan = self.create_plan(
            "Resolver Priority Plan",
            "2026-01-01",
        )

        low_priority_rule = self.create_rule(
            "Resolver Priority 100",
            plan,
            based_on="Item",
            item=self.item,
            priority=100,
        )

        high_priority_rule = self.create_rule(
            "Resolver Priority 10",
            plan,
            based_on="Item",
            item=self.item,
            priority=10,
        )

        transaction = {
            "item": self.item,
        }

        matches = get_matching_rules(
            transaction,
            plan,
        )

        self.assertEqual(
            matches[0].name,
            high_priority_rule.name,
        )

        self.assertEqual(
            matches[1].name,
            low_priority_rule.name,
        )

    def test_rule_tiers_are_loaded(self):
        plan = self.create_plan(
            "Resolver Tier Plan",
            "2026-01-01",
        )

        rule = self.create_rule(
            "Resolver Tier Rule",
            plan,
            based_on="Item",
            item=self.item,
        )

        rule.calculation_method = "Tiered"

        rule.append(
            "tiers",
            {
                "from_amount": 0,
                "to_amount": 1000,
                "rate": 5,
            },
        )

        rule.append(
            "tiers",
            {
                "from_amount": 1000,
                "to_amount": 5000,
                "rate": 10,
            },
        )

        rule.save()

        tiers = get_rule_tiers(rule.name)

        self.assertEqual(len(tiers), 2)
        self.assertEqual(tiers[0]["from_amount"], 0)
        self.assertEqual(tiers[0]["to_amount"], 1000)
        self.assertEqual(tiers[0]["rate"], 5)

    def test_commission_payee_is_resolved(self):
        payee = frappe.get_doc(
            {
                "doctype": "Commission Payee",
                "payee_name": "Resolver Test Payee",
                "payee_type": "Employee",
                "sales_person": self.sales_person,
                "enabled": 1,
            }
        )

        payee.insert()

        result = get_commission_payee(self.sales_person)

        self.assertEqual(
            result,
            payee.name,
        )

    def test_disabled_commission_payee_is_ignored(self):
        sales_person = self._create_sales_person("Resolver Disabled Payee Sales Person")

        payee = frappe.get_doc(
            {
                "doctype": "Commission Payee",
                "payee_name": "Resolver Disabled Payee",
                "payee_type": "Employee",
                "sales_person": sales_person,
                "enabled": 0,
            }
        )
        payee.insert()

        result = get_commission_payee(sales_person)

        self.assertIsNone(result)

    def test_missing_commission_payee_returns_none(self):
        result = get_commission_payee("Nonexistent Sales Person")

        self.assertIsNone(result)
