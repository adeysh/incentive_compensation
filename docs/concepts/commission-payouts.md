# Commission Payouts

A Commission Payout represents the actual payment of a Commission Statement.

A payout is created from a Posted Commission Statement and tracks the process of paying the approved commission amount to the Commission Payee.

The Commission Statement represents the approved commission.

The Commission Payout represents the payment of that commission.

## Purpose

The payout stage separates commission approval from actual payment.

The overall flow is:

```text
Commission Statement
        ↓
      Posted
        ↓
Commission Payout
        ↓
   Processing
        ↓
      Paid
```

This separation allows the application to track whether an approved commission has actually been paid.

## Fields

| Field                | Description                                 |
| -------------------- | ------------------------------------------- |
| Commission Statement | Statement from which the payout was created |
| Commission Payee     | Person or partner receiving the payment     |
| Company              | Company making the payment                  |
| Currency             | Currency of the payout                      |
| Amount               | Amount being paid                           |
| Payment Date         | Date on which the payment was made          |
| Payment Reference    | Reference identifying the payment           |
| Status               | Current payout lifecycle state              |

The statement, payee, company, currency, and amount are derived from the Posted Commission Statement and are not intended to be manually changed.

## Creating a Payout

A payout can be created from a **Posted Commission Statement**.

For example:

```text
Commission Statement
Net Commission: ₹1,500
Status: Posted
```

Creating the payout produces:

```text
Commission Payout
Amount: ₹1,500
Status: Pending
```

The payout inherits the relevant statement information.

## Payout Lifecycle

A Commission Payout follows an explicit workflow:

```text
Pending
   ↓
Processing
   ↓
Paid
```

It can also move through failure or cancellation states:

```text
Pending
   ├──→ Processing
   └──→ Cancelled

Processing
   ├──→ Paid
   └──→ Failed

Failed
   ├──→ Processing
   └──→ Cancelled
```

Each state represents a different point in the payment process.

## Pending

A newly created payout starts as:

```text
Pending
```

This means the payout has been created but payment processing has not yet begun.

The payout is associated with a Posted Commission Statement.

## Processing

When payment processing begins, move the payout to:

```text
Processing
```

This indicates that the payment is being processed but has not yet been confirmed as paid.

## Paid

When the payment has actually been made, enter the required payment information:

- Payment Date
- Payment Reference

Then mark the payout as:

```text
Paid
```

The associated Commission Statement is also marked as:

```text
Paid
```

This keeps the statement and payout lifecycles synchronized.

## Payment Information

Before a payout can be marked Paid, the payment details must be provided.

### Payment Date

The Payment Date records when the payment was made.

For example:

```text
Payment Date: 2026-10-05
```

### Payment Reference

The Payment Reference identifies the actual payment transaction.

For example:

```text
Payment Reference: UTR-TEST-0001
```

The reference could represent a bank transaction identifier or another payment reference used by the organization.

Both fields are required before the payout can be marked Paid.

## Why Payment Details Are Required

A payout should not simply be marked Paid without evidence of the payment.

Requiring:

```text
Payment Date
+
Payment Reference
```

creates a basic audit trail for the actual payment.

The resulting history is:

```text
Commission Calculation
        ↓
Commission Statement
        ↓
Approved
        ↓
Posted
        ↓
Payout
        ↓
Payment Date + Reference
        ↓
Paid
```

## Statement and Payout Relationship

A Commission Payout belongs to a specific Commission Statement.

The relationship is:

```text
Commission Statement
        │
        └── Commission Payout
```

The payout amount comes from the statement's net commission.

For example:

```text
Statement Net Commission = ₹500
                ↓
Payout Amount             = ₹500
```

The payout therefore does not independently recalculate the commission.

The statement is the source of the amount being paid.

## One Payout per Active Statement

The application prevents multiple active payouts from being created for the same Commission Statement.

This helps prevent accidentally paying the same statement more than once.

Conceptually:

```text
Posted Statement
      │
      └── Active Payout
```

A second active payout for the same statement is not allowed.

This protects the payment process from duplicate payouts.

## Payout Amount

The payout amount is based on the statement's **Net Commission**.

For example:

```text
Gross Commission = ₹2,000
Adjustments      = -₹200
Net Commission   = ₹1,800
```

The payout amount is:

```text
₹1,800
```

The payout does not recalculate the underlying commission rules or ledger entries.

## Failed Payments

A payout can enter:

```text
Failed
```

when payment processing does not succeed.

A failed payout can be moved back to:

```text
Processing
```

when payment processing is attempted again.

Alternatively, it can be cancelled when the payout should no longer proceed.

The lifecycle therefore supports recovery from payment failures without changing the original commission calculation.

## Cancellation

A Pending or Failed payout can be cancelled according to the payout workflow.

Cancellation prevents the payout from continuing through the normal payment process.

The original Commission Statement remains a historical record of the approved commission.

## Payout Does Not Change the Ledger

The Commission Ledger records the commission calculation.

The Commission Statement records the approved grouping of ledger entries.

The Commission Payout records the payment.

These responsibilities remain separate:

```text
Commission Ledger
    → What was calculated?

Commission Statement
    → What was approved for the period?

Commission Payout
    → What was actually paid?
```

Marking a payout as Paid does not modify the original Commission Ledger calculation.

## Example

Suppose a salesperson has a Posted Commission Statement:

```text
Commission Payee: Test Salesperson
Net Commission:   ₹500
Status:           Posted
```

Create a payout:

```text
Amount: ₹500
Status: Pending
```

Start processing:

```text
Pending
   ↓
Processing
```

Enter:

```text
Payment Date:      2026-10-05
Payment Reference: UTR-TEST-0001
```

Then mark the payout as Paid:

```text
Processing
   ↓
Paid
```

The associated statement becomes:

```text
Paid
```

The complete process is now:

```text
Sales Invoice
      ↓
Commission Ledger
      ↓
Commission Statement
      ↓
Generated
      ↓
Under Review
      ↓
Approved
      ↓
Posted
      ↓
Commission Payout
      ↓
Processing
      ↓
Paid
```

## Best Practices

### Create Payouts Only From Posted Statements

A statement should complete its review and approval process before payment begins.

The normal sequence is:

```text
Generated
    ↓
Under Review
    ↓
Approved
    ↓
Posted
    ↓
Create Payout
```

### Record Payment Details

Always provide the Payment Date and Payment Reference before marking a payout Paid.

### Do Not Manually Change Derived Fields

The statement, payee, company, currency, and payout amount come from the associated statement.

Keeping these fields controlled prevents the payout from becoming inconsistent with the approved statement.

### Treat Paid Payouts as Historical Records

Once a payout is marked Paid, it represents a completed payment event and should be treated as part of the historical audit trail.

## Next Step

The Concepts section is now complete.

Continue with [Commission Lifecycle](../workflows/commission-lifecycle.md) to see how Plans, Rules, Payees, Ledger entries, Statements, and Payouts work together from start to finish.
