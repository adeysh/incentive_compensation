import frappe


def create_ledger_entry(transaction, result):
    """
    Create a Commission Ledger entry from a commission calculation result.
    """

    source_key = get_source_key(transaction, result)

    existing = frappe.db.get_value(
        "Commission Ledger",
        {"source_key": source_key},
        "name",
    )

    if existing:
        return frappe.get_doc("Commission Ledger", existing)

    ledger = frappe.get_doc(
        {
            "doctype": "Commission Ledger",
            "sales_invoice": transaction.get("sales_invoice"),
            "sales_invoice_item": transaction.get("sales_invoice_item"),
            "source_key": source_key,
            "entry_type": "Commission",
            "commission_payee": result.get("commission_payee"),
            "commission_rule": result.get("commission_rule"),
            "commission_plan": result.get("commission_plan"),
            "company": transaction.get("company"),
            "currency": transaction.get("currency"),
            "calculation_method": result.get("calculation_method"),
            "rate": result.get("rate"),
            "commission_amount": result.get("commission_amount"),
            "base_amount": result.get("base_amount"),
            "fixed_amount": result.get("fixed_amount"),
            "status": "Calculated",
            "transaction_date": transaction.get("transaction_date"),
            "calculation_date": frappe.utils.now_datetime(),
        }
    )

    ledger.insert()

    return ledger


def create_ledger_entries_for_invoice(invoice):
    from .evaluator import evaluate_sales_invoice

    evaluations = evaluate_sales_invoice(invoice)

    ledgers = []

    for evaluation in evaluations:
        ledger = create_ledger_entry(
            evaluation["transaction"],
            evaluation["result"],
        )
        ledgers.append(ledger)

    return ledgers


def get_source_key(transaction, result):
    return "|".join(
        [
            transaction.get("sales_invoice"),
            transaction.get("sales_invoice_item"),
            result.get("commission_payee"),
            result.get("commission_rule"),
        ]
    )


def reverse_ledger_entry(ledger):
    reversal_source_key = f"{ledger.source_key}|REVERSAL"

    existing = frappe.db.get_value(
        "Commission Ledger",
        {"source_key": reversal_source_key},
        "name",
    )

    # Keep reversal creation idempotent.
    if existing:
        return frappe.get_doc("Commission Ledger", existing)

    # Do not allow an already-reversed commission to be reversed again.
    if ledger.status == "Reversed":
        frappe.throw(
            f"Commission Ledger '{ledger.name}' has already been reversed.",
            title="Commission Already Reversed",
        )

    ledger.status = "Reversed"
    ledger.save()

    reversal = frappe.get_doc(
        {
            "doctype": "Commission Ledger",
            "sales_invoice": ledger.sales_invoice,
            "sales_invoice_item": ledger.sales_invoice_item,
            "commission_payee": ledger.commission_payee,
            "commission_rule": ledger.commission_rule,
            "commission_plan": ledger.commission_plan,
            "calculation_method": ledger.calculation_method,
            "rate": ledger.rate,
            "commission_amount": -ledger.commission_amount,
            "base_amount": ledger.base_amount,
            "fixed_amount": ledger.fixed_amount,
            "status": "Calculated",
            "transaction_date": frappe.utils.today(),
            "calculation_date": frappe.utils.now_datetime(),
            "source_key": reversal_source_key,
            "reversal_of": ledger.name,
            "entry_type": "Reversal",
        }
    )

    reversal.insert()

    return reversal


def reverse_commissions_for_invoice(invoice):
    ledgers = frappe.get_all(
        "Commission Ledger",
        filters={
            "sales_invoice": invoice.name,
            "entry_type": "Commission",
            "status": ["!=", "Reversed"],
        },
        fields=["name"],
    )

    reversals = []

    for ledger_data in ledgers:
        ledger = frappe.get_doc(
            "Commission Ledger",
            ledger_data.name,
        )

        reversal = reverse_ledger_entry(ledger)

        reversals.append(reversal)

    return reversals
