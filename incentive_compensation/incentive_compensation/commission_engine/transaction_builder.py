def build_transactions_from_sales_invoice(invoice):
    transactions = []

    for item in invoice.items:
        for sales_team_member in invoice.sales_team:
            transactions.append(
                {
                    "sales_invoice": invoice.name,
                    "sales_invoice_item": item.name,
                    "transaction_date": invoice.posting_date,
                    "company": invoice.company,
                    "currency": invoice.currency,
                    "customer": invoice.customer,
                    "customer_group": invoice.customer_group,
                    "territory": invoice.territory,
                    "item": item.item_code,
                    "item_group": item.item_group,
                    "sales_person": sales_team_member.sales_person,
                    "allocated_percentage": sales_team_member.allocated_percentage,
                    "base_amount": item.net_amount,
                }
            )

    return transactions
