# Architecture

The ERPNext Incentive Compensation Engine is a Frappe application that extends ERPNext with a dedicated commission and incentive compensation lifecycle.

The architecture separates commission configuration, calculation, historical records, statement processing, payout processing, and reporting.

## High-Level Architecture

The application sits on top of Frappe and ERPNext.

```text
                    ERPNext
                       │
                       │ Sales Invoice
                       ▼
              Commission Events
                       │
                       ▼
              Commission Engine
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Resolver     Evaluator    Calculator
          │            │            │
          └────────────┼────────────┘
                       │
                       ▼
               Commission Ledger
                       │
                       ▼
             Commission Statement
                       │
                       ▼
                Commission Payout
```

The Commission Ledger is the historical record produced by the calculation process. Statements group eligible ledger entries into a period-based snapshot, and payouts track the payment of posted statements.

## Application Structure

The main application package is:

```text
incentive_compensation/
└── incentive_compensation/
    ├── commission_engine/
    ├── commission_ledger/
    ├── commission_plan/
    ├── commission_rule/
    ├── commission_payee/
    ├── commission_statement/
    ├── commission_payout/
    ├── commission_tier/
    └── ...
```

The exact Frappe-generated DocType directory structure may vary as the application evolves. The important application-level separation is between DocTypes and the reusable commission engine.

## Commission Engine

The core business logic is organized under:

```text
incentive_compensation/
└── commission_engine/
    ├── calculator.py
    ├── commission_events.py
    ├── engine.py
    ├── evaluator.py
    ├── ledger.py
    ├── payout.py
    ├── payout_workflow.py
    ├── permissions.py
    ├── resolver.py
    ├── statement.py
    ├── statement_resolver.py
    ├── statement_workflow.py
    ├── transaction_builder.py
    └── reports/
```

Each module has a focused responsibility.

### `calculator.py`

Contains the low-level commission calculation functions.

It handles calculation methods such as:

- percentage
- fixed amount
- tiered commission
- allocation

The calculator works with numeric values and returns calculated commission amounts rather than handling Frappe documents or workflow concerns.

### `resolver.py`

Resolves configuration needed for a commission calculation.

It is responsible for finding relevant:

- Commission Plans
- Commission Rules
- Commission Tiers
- Commission Payees

Plan selection considers the company and transaction date. When multiple active plans are applicable, the applicable plan with the most recent `valid_from` is selected.

Rule resolution then determines which enabled rule matches the transaction.

### `evaluator.py`

Coordinates the resolution and calculation process for a transaction.

The evaluator determines:

1. which Commission Plan applies
2. which Commission Rule matches
3. which Commission Payee receives the commission
4. which calculation method should be used
5. what commission amount should be recorded

It connects configuration resolution with commission calculation.

### `engine.py`

Provides the commission calculation layer used by the evaluator.

It applies the selected calculation method and returns the calculated result.

### `transaction_builder.py`

Converts ERPNext Sales Invoice information into commission calculation inputs.

In particular, it handles Sales Team contribution allocation.

For example:

```text
Invoice Item Amount = ₹10,000

Sales Person A = 60%
Sales Person B = 40%

A's commission base = ₹6,000
B's commission base = ₹4,000
```

The allocation is captured as part of the commission transaction processing so that the resulting ledger entries represent the transaction as it was processed.

### `ledger.py`

Creates and manages Commission Ledger entries.

The ledger layer is responsible for:

- creating commission entries
- preventing duplicate entries through the source key
- creating reversal entries
- reversing commissions when a source Sales Invoice is cancelled

The ledger represents the historical result of the commission calculation.

## Commission DocTypes

The application uses several DocTypes to represent different parts of the commission lifecycle.

### Commission Plan

Defines the overall commission configuration and validity period.

A plan belongs to a Company and Currency and has a validity period.

```text
Commission Plan
├── Plan Name
├── Company
├── Currency
├── Valid From
├── Valid To
└── Status
```

### Commission Rule

Defines when and how a commission is calculated within a plan.

Rules can be based on transaction conditions such as:

- Item
- Item Group
- Sales Person
- Customer
- Customer Group
- Territory

A rule also defines the calculation method and its associated values or tiers.

### Commission Tier

A child record used by tiered commission rules.

It defines amount ranges and the commission rate applicable to each range.

### Commission Payee

Represents the person or partner who receives commission.

The payee can represent:

- an Employee
- a Sales Partner

The payee connects the commission calculation to the corresponding ERPNext Sales Person or Sales Partner.

### Commission Ledger

Stores the historical result of a commission calculation.

Important information includes:

- source Sales Invoice
- Sales Invoice Item
- Commission Payee
- Commission Rule
- Commission Plan
- calculation method
- rate
- base amount
- fixed amount
- commission amount
- transaction date
- calculation date
- status
- source key
- reversal information
- entry type
- company
- currency

Ledger entries are immutable audit records after creation.

### Commission Statement

Groups eligible Commission Ledger entries for a particular payee, company, currency, and date range.

A statement contains:

- the selected payee
- company and currency
- date range
- gross commission
- adjustments
- net commission
- generation date
- status
- a snapshot of the included ledger entries

Once generated, the statement represents an immutable snapshot.

### Commission Statement Entry

A child record that stores the ledger entries included in a Commission Statement.

It provides the statement with a historical snapshot of the commission entries included at generation time.

### Commission Payout

Represents the payment process for a posted Commission Statement.

It contains:

- Commission Statement
- Commission Payee
- Company
- Currency
- amount
- payment date
- payment reference
- status

The payout lifecycle is separate from commission calculation and statement approval.

## Commission Calculation Flow

The main calculation path is:

```text
Sales Invoice Submitted
        │
        ▼
Commission Event
        │
        ▼
Transaction Builder
        │
        ▼
Plan Resolver
        │
        ▼
Rule Resolver
        │
        ▼
Payee Resolution
        │
        ▼
Commission Evaluator
        │
        ▼
Commission Calculator
        │
        ▼
Commission Ledger
```

The result of the calculation is stored rather than recalculated later when reports or statements are generated.

## Plan and Rule Resolution

Plan selection happens before rule evaluation.

The system looks for active plans applicable to the Company and transaction date.

When multiple applicable plans exist, the plan with the most recent `valid_from` is selected.

After the plan is selected, rules belonging to that plan are evaluated.

Rule matching uses the rule's configured condition, such as Item, Item Group, Sales Person, Customer, Customer Group, or Territory.

When multiple rules match, priority determines which rule is evaluated first.

This separation keeps plan selection independent from the detailed transaction conditions used by individual rules.

## Sales Team Allocation

ERPNext Sales Invoices can contain multiple Sales Team members.

The transaction builder uses their contribution percentages to determine each member's allocated commission base.

For example:

```text
Invoice Item
₹20,000
   │
   ├── Sales Person A: 70%
   │       Base = ₹14,000
   │
   └── Sales Person B: 30%
           Base = ₹6,000
```

Each resulting commission calculation is associated with the appropriate payee.

The allocation is part of transaction processing rather than being reconstructed later from potentially changed transaction data.

## Ledger as the Historical Boundary

The Commission Ledger is an important architectural boundary.

Configuration records such as Commission Plans and Commission Rules describe how commissions should be calculated.

The Commission Ledger records what was actually calculated.

```text
Configuration
     │
     ▼
Calculation
     │
     ▼
Historical Ledger
```

After a ledger entry is created, changing a Commission Plan or Commission Rule does not recalculate or modify that historical entry.

This provides an audit trail for commission calculations.

## Statement Architecture

Commission Statements do not recalculate individual commissions.

Instead, they resolve eligible Commission Ledger entries for:

- Commission Payee
- Company
- Currency
- date range

Ledger entries already included in another non-cancelled statement are excluded.

The selected entries are copied into the statement as child records when the statement is generated.

```text
Commission Ledger
      │
      │ eligible entries
      ▼
Statement Resolver
      │
      ▼
Commission Statement
      │
      ├── Gross Commission
      ├── Adjustments
      ├── Net Commission
      └── Ledger Entry Snapshot
```

This creates a stable statement snapshot.

## Statement Workflow

Statement generation and statement approval are intentionally separate operations.

A new statement starts as:

```text
Draft
```

Generation changes it to:

```text
Draft
  ↓
Generated
```

After generation, the approval workflow is:

```text
Generated
    ↓
Under Review
    ├──→ Cancelled
    ↓
Approved
    ├──→ Cancelled
    ↓
Posted
    ↓
Paid
```

`Draft → Generated` is a generation operation rather than a normal workflow transition.

A Posted statement is finalized and can be used to create a Commission Payout.

## Payout Architecture

A payout is created from a Posted Commission Statement.

```text
Posted Statement
       │
       ▼
Commission Payout
       │
       ▼
Pending
       │
       ▼
Processing
       │
       ├──→ Failed
       │       │
       │       └──→ Processing
       │
       └──→ Paid
```

Pending and Failed payouts can also be cancelled according to the payout workflow.

When the payout is successfully marked as Paid, the associated Commission Statement is marked as Paid.

Payment Date and Payment Reference are required before a payout can be marked as Paid.

## Reversal Architecture

Commission reversals are handled separately from the original commission entry.

When a Sales Invoice that generated commission is cancelled, the application creates reversal ledger entries rather than modifying the original commission entry.

Conceptually:

```text
Original Commission
       │
       │ source invoice cancelled
       ▼
Reversal Entry
       │
       ▼
Original + Reversal
```

The original ledger entry remains part of the historical audit trail.

The reversal entry references the original entry through `reversal_of` and records the reversal as a separate ledger event.

## Idempotency

Commission creation uses a source key to prevent duplicate ledger entries for the same source calculation.

This is important because ERPNext document events may be triggered more than once during normal application operation or retries.

The source key provides a stable identity for the commission calculation and prevents the same calculation from being inserted repeatedly.

## Immutability

Historical financial records are protected from ordinary modification.

The Commission Ledger is immutable after creation.

Generated Commission Statements are also protected from modification of their historical calculation data and included ledger entries.

This ensures that:

```text
Calculated Result
       ↓
Historical Record
       ↓
Audit Trail
```

remains stable even when configuration changes later.

## Permissions and Workflow Protection

Workflow-related operations are protected in the commission engine.

The application separates ordinary document operations from controlled workflow transitions.

For example, a Commission Statement cannot simply be changed from `Generated` to `Posted` by directly editing its status.

Instead, the appropriate workflow transition must be used.

Protected operations require the appropriate Commission Manager role.

This prevents users from bypassing the intended commission lifecycle through direct API calls or document edits.

## Reports

Reporting is built around Commission Ledger data.

The application provides:

- Commission Summary
- Commission by Payee
- Commission by Plan
- Commission by Rule
- Commission by Invoice
- Commission by Date

Reports do not need to recalculate historical commissions because the calculated result is already stored in the ledger.

This keeps reporting separate from the calculation engine.

## Separation of Responsibilities

The architecture intentionally separates four major concerns.

### Configuration

Defines what should happen.

```text
Commission Plan
Commission Rule
Commission Tier
Commission Payee
```

### Calculation

Determines what commission applies to a transaction.

```text
Transaction Builder
Resolver
Evaluator
Calculator
```

### Historical Processing

Records what actually happened.

```text
Commission Ledger
Commission Statement
Commission Statement Entry
```

### Payment Processing

Tracks the payment of finalized commission.

```text
Commission Payout
```

This separation makes the system easier to reason about and protects historical records from configuration changes.

## End-to-End Data Flow

Putting the main components together:

```text
                    ERPNext Sales Invoice
                             │
                             ▼
                    Commission Event
                             │
                             ▼
                    Transaction Builder
                             │
                             ▼
                     Plan / Rule Resolver
                             │
                             ▼
                        Payee Resolver
                             │
                             ▼
                         Evaluator
                             │
                             ▼
                         Calculator
                             │
                             ▼
                    Commission Ledger
                             │
                 ┌───────────┴───────────┐
                 │                       │
                 ▼                       ▼
             Reports              Statement Resolver
                                         │
                                         ▼
                               Commission Statement
                                         │
                                         ▼
                                      Posted
                                         │
                                         ▼
                                Commission Payout
                                         │
                                         ▼
                                        Paid
```

## Design Principles

The architecture follows several principles:

### Keep calculation separate from storage

Calculation functions determine commission amounts. Ledger functions persist the historical result.

### Treat the ledger as an audit boundary

Once calculated, a commission should be represented by a stable historical record.

### Use explicit workflows

Statements and payouts should move through controlled lifecycle transitions rather than unrestricted status changes.

### Preserve source context

Commission entries retain references to their source Sales Invoice and the configuration used for the calculation.

### Make processing idempotent

A source key prevents duplicate commission ledger entries.

### Separate calculation from payment

Calculating a commission, approving it, and paying it are different business operations and are represented separately.

## Development Entry Points

When working on the codebase, the following modules are useful starting points:

| Area                          | Module                                     |
| ----------------------------- | ------------------------------------------ |
| Commission calculations       | `commission_engine/calculator.py`          |
| Plan/rule/payee resolution    | `commission_engine/resolver.py`            |
| Calculation orchestration     | `commission_engine/evaluator.py`           |
| Sales transaction preparation | `commission_engine/transaction_builder.py` |
| Ledger creation/reversal      | `commission_engine/ledger.py`              |
| ERPNext event integration     | `commission_engine/commission_events.py`   |
| Statement generation          | `commission_engine/statement.py`           |
| Statement entry resolution    | `commission_engine/statement_resolver.py`  |
| Statement workflow            | `commission_engine/statement_workflow.py`  |
| Payout creation               | `commission_engine/payout.py`              |
| Payout workflow               | `commission_engine/payout_workflow.py`     |
| API role protection           | `commission_engine/permissions.py`         |
| Reports                       | `commission_engine/reports/`               |

## Next Step

Continue with [Calculation Engine](calculation-engine.md) to understand how commission amounts are calculated from the resolved plan, rule, transaction base, and calculation method.
