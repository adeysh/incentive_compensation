# Events

The ERPNext Incentive Compensation Engine uses Frappe document events to connect ERPNext Sales Invoice activity with commission processing.

The event layer is intentionally small. It acts as the integration boundary between ERPNext documents and the commission engine rather than containing the commission calculation logic itself.

## Event Flow

The primary event flow is:

```text
ERPNext Sales Invoice
        │
        ├── Submit
        │     ↓
        │  Commission Event
        │     ↓
        │  Create Commission Ledger Entries
        │
        └── Cancel
              ↓
           Commission Event
              ↓
           Create Reversal Entries
```

The application currently uses Sales Invoice submission and cancellation as the source events for automatic commission processing.

## Event Module

The event handlers are located in:

```text
incentive_compensation/
└── incentive_compensation/
    └── commission_engine/
        └── commission_events.py
```

The module contains the event handlers that connect Frappe document lifecycle events to the commission engine.

The main handlers are:

```text
on_sales_invoice_submit()
on_sales_invoice_cancel()
```

## Sales Invoice Submission

When a Sales Invoice is submitted, the application starts commission processing.

The submission handler delegates to the ledger layer:

```text
Sales Invoice Submitted
        ↓
on_sales_invoice_submit()
        ↓
create_ledger_entries_for_invoice()
        ↓
Commission Calculation
        ↓
Commission Ledger
```

The event handler itself does not determine the commission rate or perform the calculation.

That responsibility remains in the commission engine.

This keeps the event layer thin and makes the calculation logic reusable and easier to test.

## Why Submission Triggers Commission Calculation

A submitted Sales Invoice represents a finalized sales transaction in ERPNext.

The commission engine uses this point in the document lifecycle to calculate and record the commission associated with the transaction.

The resulting Commission Ledger entry represents the commission calculated from that source transaction.

Conceptually:

```text
Draft Sales Invoice
       ↓
Submitted Sales Invoice
       ↓
Commission Calculation
       ↓
Commission Ledger
```

The commission is therefore tied to the submitted transaction rather than an arbitrary document save.

## Sales Invoice Cancellation

Sales Invoice cancellation is handled separately from submission.

When a Sales Invoice that has generated commissions is cancelled, the application creates corresponding reversal ledger entries.

The flow is:

```text
Sales Invoice Cancelled
        ↓
on_sales_invoice_cancel()
        ↓
reverse_commissions_for_invoice()
        ↓
Reversal Ledger Entries
```

The original Commission Ledger entries are not modified or deleted.

Instead, the cancellation is represented as a separate reversal event.

## Why Reversals Are Separate

The Commission Ledger is designed as a historical audit record.

Changing the original commission entry when an invoice is cancelled would destroy information about what was originally calculated.

Instead, the system preserves the original entry and records the cancellation separately:

```text
Original Commission
       ₹500
         │
         │ Invoice cancelled
         ▼
Reversal
      -₹500
```

The reversal entry references the original commission through `reversal_of`.

This creates an auditable sequence of events.

## Event-to-Engine Separation

The event layer and calculation engine have different responsibilities.

### Event Layer

Determines:

- when commission processing should happen
- which source document caused the processing

### Commission Engine

Determines:

- which plan applies
- which rule matches
- who receives the commission
- what the calculation base is
- which calculation method applies
- how much commission should be recorded

Conceptually:

```text
Frappe Event
     │
     ▼
Commission Engine
     │
     ├── Resolve
     ├── Evaluate
     ├── Calculate
     └── Record
```

This separation prevents ERPNext-specific event handling from becoming tightly coupled to commission calculation logic.

## Submit Event

The submit handler is intentionally simple:

```python
def on_sales_invoice_submit(doc, method=None):
    create_ledger_entries_for_invoice(doc)
```

The `doc` argument is the submitted Sales Invoice.

The optional `method` argument is compatible with Frappe document event handler conventions.

The handler delegates the actual work to:

```text
create_ledger_entries_for_invoice()
```

That function belongs to the ledger layer and is responsible for starting commission entry creation for the invoice.

## Cancel Event

The cancellation handler follows the same pattern:

```python
def on_sales_invoice_cancel(doc, method=None):
    reverse_commissions_for_invoice(doc)
```

The event handler delegates reversal processing to:

```text
reverse_commissions_for_invoice()
```

The reversal logic therefore remains outside the event module.

## Event Hooks

The event handlers need to be registered against the corresponding ERPNext document events.

Conceptually, the application connects:

```text
Sales Invoice
    │
    ├── on_submit  → on_sales_invoice_submit
    │
    └── on_cancel  → on_sales_invoice_cancel
```

Frappe's document event system is what allows the custom application to react to ERPNext document lifecycle events without modifying ERPNext core code.

The application therefore extends ERPNext behavior through its own hooks.

## Why Use Frappe Hooks

Using Frappe hooks provides several architectural advantages:

- ERPNext core code remains unchanged.
- Commission processing is isolated in the custom application.
- The integration follows the Frappe application model.
- The event handlers can be maintained independently from ERPNext.
- The commission engine can evolve without modifying the Sales Invoice implementation.

The integration point is therefore:

```text
ERPNext Core
     │
     │ Frappe Event
     ▼
Custom Application
```

## Idempotency at the Event Boundary

Document events should not be treated as a guarantee that processing will only ever be attempted once.

The commission engine therefore protects ledger creation with a source key.

The important distinction is:

```text
Event Handler
    ↓
May be invoked more than once
    ↓
Ledger layer checks source identity
    ↓
Duplicate commission is prevented
```

The event layer triggers processing, while the ledger layer ensures that the same calculation is not recorded repeatedly.

This makes idempotency a persistence concern rather than an assumption made by the event handler.

## Source Key

Commission Ledger creation uses a `source_key` to identify a commission calculation.

Conceptually:

```text
Source Transaction
       +
Calculation Context
       ↓
Source Key
       ↓
Commission Ledger
```

Before creating a new ledger entry, the ledger layer can determine whether the corresponding source calculation has already been recorded.

If it already exists, another copy should not be created.

## Event Processing and Sales Team

A Sales Invoice may contain multiple Sales Team members.

The submit event passes the Sales Invoice into the commission processing pipeline.

The transaction builder then handles the Sales Team allocation.

For example:

```text
Sales Invoice
    │
    ├── Item ₹20,000
    │
    └── Sales Team
          ├── Person A — 70%
          └── Person B — 30%
```

The event handler does not calculate these allocations itself.

Instead:

```text
Sales Invoice Event
       ↓
Transaction Builder
       ↓
Allocated Commission Inputs
       ↓
Commission Engine
       ↓
Ledger Entries
```

This keeps transaction preparation separate from event handling.

## Event Processing and Commission Plans

The Sales Invoice event does not directly select a Commission Plan.

Plan resolution occurs inside the commission engine.

The flow is:

```text
Sales Invoice Submitted
        ↓
Event Handler
        ↓
Commission Processing
        ↓
Applicable Company / Date
        ↓
Commission Plan Resolution
```

This allows plan-selection rules to remain centralized in `resolver.py`.

## Event Processing and Commission Rules

The same principle applies to Commission Rules.

The event handler does not know whether the rule is based on:

- Item
- Item Group
- Sales Person
- Customer
- Customer Group
- Territory

It simply starts commission processing.

The resolver and evaluator determine which rule applies.

## Event Processing and Payees

Payee resolution also belongs to the commission engine.

The event layer does not need to know whether the commission recipient is an Employee or Sales Partner.

Instead:

```text
Sales Invoice
     ↓
Sales Team / transaction context
     ↓
Payee Resolution
     ↓
Commission Payee
```

The resolved payee is then stored on the Commission Ledger entry.

## Error Handling

Because the submit event starts commission processing, errors raised by the commission engine can affect the document operation that triggered the event.

This is important when developing or debugging the integration.

When investigating a failed Sales Invoice submission, check:

```text
1. Sales Invoice data
2. Sales Team allocation
3. Applicable Commission Plan
4. Matching Commission Rule
5. Commission Payee
6. Calculation
7. Ledger creation
```

The event handler is usually only the entry point; the actual error may originate deeper in the commission engine.

## Debugging Event Processing

When a submitted Sales Invoice does not produce a commission, inspect the pipeline in order.

### 1. Confirm the Invoice Was Submitted

The commission submit event is tied to Sales Invoice submission.

### 2. Check Sales Team

Confirm that the invoice has the expected Sales Person and contribution percentage.

### 3. Check the Plan

Verify that an active Commission Plan applies to the Company and transaction date.

### 4. Check the Rule

Verify that an enabled Commission Rule matches the transaction.

### 5. Check the Payee

Verify that the Sales Person can be resolved to the configured Commission Payee.

### 6. Check the Calculation

Verify the base amount, calculation method, rate, fixed amount, or tier configuration.

### 7. Check the Ledger

If calculation succeeds, verify that the Commission Ledger entry was created.

This follows the same order as the application's processing architecture.

## Cancellation Debugging

If cancelling a Sales Invoice does not produce a reversal, inspect:

```text
1. Was the original invoice commission recorded?
2. Does the original ledger entry reference the invoice?
3. Was the invoice actually cancelled?
4. Was reversal processing triggered?
5. Was a reversal already created?
```

The original ledger entry should remain unchanged.

The expected result is a separate reversal entry.

## Event and Historical Integrity

Events are responsible for creating historical records at meaningful points in the ERPNext document lifecycle.

The submit event creates the commission record.

The cancellation event creates the corresponding reversal.

This produces a historical sequence such as:

```text
Sales Invoice Submitted
        ↓
Commission Calculated
        ↓
Commission Ledger Created
        ↓
Sales Invoice Cancelled
        ↓
Commission Reversed
```

The history is therefore represented by separate records rather than destructive updates.

## Testing Event Handlers

Event behavior should be tested at more than one level.

### Unit-Level Tests

Test the underlying calculation and ledger functions independently.

Examples include:

- commission calculation
- rule matching
- ledger creation
- duplicate prevention
- reversal creation

### Integration Tests

Test that the Frappe document event actually invokes the intended commission processing.

For example:

```text
Create Sales Invoice
       ↓
Submit
       ↓
Commission Ledger exists
```

And for cancellation:

```text
Submit Sales Invoice
       ↓
Commission Ledger exists
       ↓
Cancel Invoice
       ↓
Reversal Ledger exists
```

### End-to-End Tests

An end-to-end test should verify the full lifecycle from source transaction through statement and payout processing.

The event portion of the flow is:

```text
Sales Invoice
       ↓
Submit
       ↓
Commission Ledger
       ↓
Statement
       ↓
Payout
```

and cancellation should verify:

```text
Sales Invoice
       ↓
Submit
       ↓
Original Commission
       ↓
Cancel
       ↓
Reversal
```

## Design Principles

The event architecture follows several principles.

### Keep handlers thin

Event handlers should delegate work rather than implement business logic.

### Keep ERPNext integration at the boundary

Sales Invoice-specific event handling belongs at the integration boundary, while commission logic belongs in the commission engine.

### Do not modify ERPNext core

The application extends ERPNext through Frappe hooks rather than changing ERPNext source code.

### Make processing idempotent

The event layer should be safe even when the same processing operation is attempted more than once.

### Preserve history

Cancellation creates reversal records rather than rewriting the original commission calculation.

### Centralize business rules

Plan, rule, payee, and calculation logic should remain in the resolver/evaluator/calculator layers instead of being duplicated in event handlers.

## Development Entry Points

When working on event-driven commission processing, these are the most useful files to inspect:

| File                                       | Responsibility                         |
| ------------------------------------------ | -------------------------------------- |
| `commission_engine/commission_events.py`   | Sales Invoice event handlers           |
| `commission_engine/ledger.py`              | Commission creation and reversal       |
| `commission_engine/transaction_builder.py` | Sales Invoice transaction preparation  |
| `commission_engine/resolver.py`            | Plan, rule, tier, and payee resolution |
| `commission_engine/evaluator.py`           | Commission evaluation                  |
| `commission_engine/calculator.py`          | Mathematical calculation               |
| `hooks.py`                                 | Application event registration         |

## Next Step

Continue with [Testing](testing.md) to understand the application's test structure, test layers, end-to-end testing, and how to run the test suite.
