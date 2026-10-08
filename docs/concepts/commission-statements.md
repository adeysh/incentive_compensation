# Commission Statements

A Commission Statement groups eligible Commission Ledger entries for a specific payee, company, currency, and date range.

It creates a period-based snapshot of commissions that can then be reviewed, approved, posted, and eventually paid.

## Purpose

A Commission Ledger records individual commission calculations.

A Commission Statement brings those calculations together into a single reviewable amount.

The relationship is:

```text
Commission Ledger
      │
      ├── Entry 1
      ├── Entry 2
      ├── Entry 3
      └── Entry 4
             │
             ▼
      Commission Statement
```

This separation allows the application to calculate commissions at transaction time while handling review and payment as a separate business process.

## Fields

| Field            | Description                                          |
| ---------------- | ---------------------------------------------------- |
| Commission Payee | Person or partner receiving the commission           |
| Company          | Company for which the statement is generated         |
| Currency         | Currency of the commission                           |
| From Date        | Beginning of the statement period                    |
| To Date          | End of the statement period                          |
| Gross Commission | Total commission included in the statement           |
| Adjustments      | Adjustments included in the statement                |
| Net Commission   | Final commission amount represented by the statement |
| Status           | Current statement lifecycle state                    |
| Generation Date  | Date and time when the statement was generated       |
| Ledger Entries   | Commission Ledger entries included in the statement  |

## Creating a Statement

A new Commission Statement starts as a Draft.

When creating the statement, specify:

```text
Commission Payee
Company
Currency
From Date
To Date
```

For example:

| Field            | Example          |
| ---------------- | ---------------- |
| Commission Payee | Test Salesperson |
| Company          | Your Company     |
| Currency         | INR              |
| From Date        | 2026-10-01       |
| To Date          | 2026-10-31       |

Save the statement.

The statement remains in:

```text
Draft
```

At this stage, the statement has selection criteria but has not yet captured its commission entries.

## Generating a Statement

After a Draft statement has been saved, use **Generate Statement**.

Generation finds eligible Commission Ledger entries matching the statement criteria.

The matching criteria are:

- Commission Payee
- Company
- Currency
- transaction date range

The application also excludes ledger entries that have already been included in another non-cancelled Commission Statement.

Conceptually:

```text
Draft Statement
      ↓
Find eligible Ledger Entries
      ↓
Calculate Statement Totals
      ↓
Store Ledger Entries
      ↓
Set Generation Date
      ↓
Generated
```

A statement cannot be generated if no eligible Commission Ledger entries are found.

## Statement Snapshot

Generation creates a snapshot of the selected commission entries.

For example, suppose the eligible ledger entries are:

```text
CL-2026-00001 → ₹500
CL-2026-00002 → ₹750
CL-2026-00003 → ₹250
```

The generated statement stores references to those ledger entries.

The resulting totals are:

```text
Gross Commission = ₹1,500
Adjustments      = ₹0
Net Commission   = ₹1,500
```

The generation date records when this snapshot was created.

## Why Statements Are Snapshots

A Commission Statement should represent what was selected for review at the time it was generated.

After generation, the statement and its ledger-entry snapshot are immutable.

This prevents the contents of an already-generated statement from changing unexpectedly because of later configuration or transaction changes.

The original Commission Ledger entries also remain immutable.

Together, they provide two levels of history:

```text
Commission Ledger
    ↓
Historical calculation

Commission Statement
    ↓
Historical grouping of calculations
```

## Statement Lifecycle

A Commission Statement follows an explicit lifecycle:

```text
Draft
  ↓
Generated
  ↓
Under Review
  ↓
Approved
  ↓
Posted
  ↓
Paid
```

Each stage has a different purpose.

### Draft

The statement is being configured.

The payee, company, currency, and date range can be selected.

The statement has not yet captured its ledger entries.

### Generated

The application has found eligible ledger entries and created the statement snapshot.

The statement totals and ledger entries are now available for review.

### Under Review

The generated statement has been submitted for review.

The commission amount and included transactions can be examined before approval.

### Approved

The statement has passed review.

It is ready to be posted.

### Posted

The statement has been finalized and can be used to create a Commission Payout.

### Paid

The associated payout has been marked as paid.

## Workflow Transitions

The statement workflow allows these transitions:

```text
Generated
    ↓
Under Review

Under Review
    ├──→ Approved
    └──→ Cancelled

Approved
    ├──→ Posted
    └──→ Cancelled

Posted
    ↓
Paid
```

A statement cannot arbitrarily jump between states.

For example, an Under Review statement cannot be directly changed to Paid.

It must progress through the defined workflow.

## Review and Approval

The statement workflow deliberately separates calculation from approval.

The commission is calculated before the statement reaches the review stage:

```text
Sales Invoice
      ↓
Commission Calculation
      ↓
Commission Ledger
      ↓
Commission Statement
      ↓
Review
      ↓
Approval
```

This means reviewers are approving a stored commission snapshot rather than triggering a new calculation.

## Statement Totals

A generated statement contains three main financial totals:

### Gross Commission

The total commission represented by the included ledger entries before adjustments.

### Adjustments

Any adjustment amount represented by the statement.

### Net Commission

The final commission amount represented by the statement.

Conceptually:

```text
Net Commission
    =
Gross Commission
    +
Adjustments
```

For a statement without adjustments:

```text
Gross Commission = ₹1,500
Adjustments      = ₹0
Net Commission   = ₹1,500
```

## Ledger Entry Selection

The statement resolver looks for ledger entries matching:

```text
Commission Payee
Company
Currency
From Date
To Date
```

Only eligible ledger statuses are considered.

Ledger entries already included in another non-cancelled statement are excluded.

This prevents the same commission from being included in multiple active statements.

For example:

```text
Ledger Entry A
      ↓
Statement 1
```

After Statement 1 has captured the entry, another statement for the same payee and period will not include that entry again while Statement 1 remains non-cancelled.

## Draft Statements and Ledger Entries

A Draft statement does not consume Commission Ledger entries.

The statement only begins to capture its ledger entries when **Generate Statement** is executed successfully.

This means it is possible to create a Draft, review its selection criteria, and generate it later without reserving the underlying ledger entries.

## Cancellation

Statements can be cancelled from the workflow at the appropriate stages.

A cancelled statement does not continue through the normal approval and payout process.

Its cancellation also means that its previously selected ledger entries are no longer considered consumed by that statement when determining eligibility for a future statement.

This allows eligible commissions to be included in a replacement statement when appropriate.

## Statement and Payout

A Commission Payout can only be created from a Posted Commission Statement.

The payout amount is based on the statement's net commission.

For example:

```text
Statement
Net Commission = ₹1,500

        ↓

Commission Payout
Amount = ₹1,500
```

The statement therefore represents the approved commission amount, while the payout represents the actual payment process.

## Example

Suppose a salesperson has the following eligible ledger entries during October:

```text
Invoice A → ₹500
Invoice B → ₹750
Invoice C → ₹250
```

Create a statement:

```text
Commission Payee: Test Salesperson
Company:          Your Company
Currency:         INR
From Date:        2026-10-01
To Date:          2026-10-31
```

After generation:

```text
Gross Commission = ₹1,500
Adjustments      = ₹0
Net Commission   = ₹1,500
Status           = Generated
```

The statement can then move through:

```text
Generated
    ↓
Under Review
    ↓
Approved
    ↓
Posted
```

A payout can then be created for:

```text
₹1,500
```

After the payout is processed and marked Paid, the statement becomes Paid.

## Immutability

Once a statement has been generated, its core configuration and calculated results are locked.

The application protects:

- Commission Payee
- Company
- Currency
- From Date
- To Date
- Gross Commission
- Adjustments
- Net Commission
- Generation Date
- Ledger Entries

The purpose is to ensure that the statement remains an accurate historical snapshot of what was generated for review.

## Best Practices

### Generate Only When the Period Is Ready

Before generating a statement, make sure the relevant commission transactions have been processed.

Generation captures the eligible ledger entries available at that time.

### Review the Included Ledger Entries

After generation, inspect the ledger entries included in the statement before submitting it for review.

### Do Not Modify Generated Statements

Once generated, treat the statement as a historical snapshot.

If the statement needs to be replaced, use the appropriate cancellation workflow and generate a new statement when appropriate.

### Use Clear Date Ranges

Use statement periods that match the organization's commission cycle, such as:

```text
Monthly
Quarterly
```

or another clearly defined business period.

## Next Step

Once a Commission Statement has been Posted, a Commission Payout can be created to track the actual payment.

Continue with [Commission Payouts](commission-payouts.md).
