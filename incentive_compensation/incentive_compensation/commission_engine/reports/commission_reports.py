import frappe


def _aggregate_entries(entries, group_field=None):
    """
    Aggregate commission ledger entries.

    Commission entries contribute to gross commission.
    Reversal and Adjustment entries contribute to adjustments.
    Net commission is gross commission plus adjustments.
    """

    if group_field is None:
        gross_commission = 0
        adjustments = 0

        for entry in entries:
            amount = entry.commission_amount or 0

            if entry.entry_type == "Commission":
                gross_commission += amount

            elif entry.entry_type in ("Reversal", "Adjustment"):
                adjustments += amount

        return {
            "gross_commission": gross_commission,
            "adjustments": adjustments,
            "net_commission": gross_commission + adjustments,
        }

    totals = {}

    for entry in entries:
        group_value = entry.get(group_field)
        amount = entry.commission_amount or 0

        if group_value not in totals:
            totals[group_value] = {
                "gross_commission": 0,
                "adjustments": 0,
            }

        if entry.entry_type == "Commission":
            totals[group_value]["gross_commission"] += amount

        elif entry.entry_type in ("Reversal", "Adjustment"):
            totals[group_value]["adjustments"] += amount

    results = []

    for group_value, values in totals.items():
        results.append(
            {
                group_field: group_value,
                "gross_commission": values["gross_commission"],
                "adjustments": values["adjustments"],
                "net_commission": (values["gross_commission"] + values["adjustments"]),
            }
        )

    return results


def _get_ledger_entries(
    company=None,
    commission_payee=None,
    from_date=None,
    to_date=None,
    group_field=None,
):
    filters = {}

    if company:
        filters["company"] = company

    if commission_payee:
        filters["commission_payee"] = commission_payee

    if from_date and to_date:
        filters["transaction_date"] = [
            "between",
            [from_date, to_date],
        ]

    fields = [
        "commission_amount",
        "entry_type",
    ]

    if group_field:
        fields.append(group_field)

    return frappe.get_all(
        "Commission Ledger",
        filters=filters,
        fields=fields,
    )


def get_commission_summary(
    company=None,
    commission_payee=None,
    from_date=None,
    to_date=None,
):
    entries = _get_ledger_entries(
        company=company,
        commission_payee=commission_payee,
        from_date=from_date,
        to_date=to_date,
    )

    return _aggregate_entries(entries)


def get_commission_by_payee(
    company=None,
    from_date=None,
    to_date=None,
):
    entries = _get_ledger_entries(
        company=company,
        from_date=from_date,
        to_date=to_date,
        group_field="commission_payee",
    )

    results = _aggregate_entries(
        entries,
        "commission_payee",
    )

    results.sort(
        key=lambda row: row["net_commission"],
        reverse=True,
    )

    return results


def get_commission_by_plan(
    company=None,
    from_date=None,
    to_date=None,
):
    entries = _get_ledger_entries(
        company=company,
        from_date=from_date,
        to_date=to_date,
        group_field="commission_plan",
    )

    results = _aggregate_entries(
        entries,
        "commission_plan",
    )

    results.sort(
        key=lambda row: row["net_commission"],
        reverse=True,
    )

    return results


def get_commission_by_rule(
    company=None,
    from_date=None,
    to_date=None,
):
    entries = _get_ledger_entries(
        company=company,
        from_date=from_date,
        to_date=to_date,
        group_field="commission_rule",
    )

    results = _aggregate_entries(
        entries,
        "commission_rule",
    )

    results.sort(
        key=lambda row: row["net_commission"],
        reverse=True,
    )

    return results


def get_commission_by_invoice(
    company=None,
    from_date=None,
    to_date=None,
):
    entries = _get_ledger_entries(
        company=company,
        from_date=from_date,
        to_date=to_date,
        group_field="sales_invoice",
    )

    results = _aggregate_entries(
        entries,
        "sales_invoice",
    )

    results.sort(
        key=lambda row: row["net_commission"],
        reverse=True,
    )

    return results


def get_commission_by_date(
    company=None,
    from_date=None,
    to_date=None,
):
    entries = _get_ledger_entries(
        company=company,
        from_date=from_date,
        to_date=to_date,
        group_field="transaction_date",
    )

    results = _aggregate_entries(
        entries,
        "transaction_date",
    )

    results.sort(
        key=lambda row: row["transaction_date"],
    )

    return results
