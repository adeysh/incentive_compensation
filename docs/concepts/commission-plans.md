# Commission Plans

A Commission Plan defines the overall commission configuration for a company.

It provides the context in which Commission Rules are evaluated and determines the period during which the plan can be used.

## Purpose

A Commission Plan answers three basic questions:

1. **Which company does this commission configuration belong to?**
2. **Which currency is used for commission calculations and payouts?**
3. **When is this plan valid?**

Commission Rules are attached to a Commission Plan and use the plan's configuration when calculating commissions.

## Fields

| Field      | Description                                           |
| ---------- | ----------------------------------------------------- |
| Plan Name  | Unique name identifying the commission plan           |
| Company    | Company for which the plan applies                    |
| Currency   | Currency used for commission calculations and payouts |
| Valid From | Date from which the plan can apply                    |
| Valid To   | Optional date after which the plan is no longer valid |
| Status     | Current state of the plan                             |

## Plan Status

A Commission Plan can have one of the following statuses:

- **Draft** — The plan is being configured and is not active.
- **Active** — The plan can be selected for eligible transactions.
- **Disabled** — The plan has been intentionally disabled.
- **Expired** — The plan's validity period has ended.

A plan must be Active and within its validity period to be considered during commission calculation.

## Validity Period

The validity period determines whether a plan can apply to a transaction.

For example:

```text
Valid From:  2026-10-01
Valid To:    2026-12-31
```

The plan can apply to transactions occurring during that period.

An empty **Valid To** creates an open-ended plan:

```text
Valid From:  2026-10-01
Valid To:    —
```

This allows the plan to remain valid until it is replaced, disabled, or otherwise no longer eligible.

## Selecting the Applicable Plan

When a Sales Invoice is processed, the commission engine first looks for active plans that:

- belong to the Sales Invoice's company
- are valid for the transaction date

If more than one active plan is valid for the same transaction date, the engine selects the plan with the most recent **Valid From** date.

For example:

```text
Plan A
Valid From: 2026-01-01

Plan B
Valid From: 2026-10-01
```

For a transaction dated:

```text
2026-10-15
```

both plans may be valid, but **Plan B** is selected because it has the more recent Valid From date.

This allows a newer commission plan to take precedence over an older plan without modifying historical transactions.

## Commission Plans and Rules

A Commission Plan does not normally determine the exact commission calculation by itself.

Instead, it provides the container and validity context for Commission Rules.

The relationship is:

```text
Commission Plan
       │
       ├── Commission Rule
       ├── Commission Rule
       └── Commission Rule
```

For example:

```text
Standard Sales Commission
│
├── Smartphone Commission — 5%
├── Laptop Commission — 7%
└── Enterprise Customer Commission — 10%
```

The Commission Rules determine which transactions qualify and how the commission is calculated.

See [Commission Rules](commission-rules.md) for the rule evaluation process.

## Changing a Plan

Commission Plans are configuration records.

Changing a plan does not recalculate existing Commission Ledger entries.

For example, if a plan previously used a 5% commission rule and the configuration is later changed, an already-created Commission Ledger entry remains unchanged.

This is intentional.

The Commission Ledger stores the historical result of the calculation so that past commissions remain auditable.

## Example

Suppose a company wants to introduce a new sales commission plan starting on October 1.

The plan could be configured as:

| Field      | Value                     |
| ---------- | ------------------------- |
| Plan Name  | Standard Sales Commission |
| Company    | Your Company              |
| Currency   | INR                       |
| Valid From | 2026-10-01                |
| Valid To   | Leave empty               |
| Status     | Active                    |

Rules can then be created under this plan to define the actual commission calculations.

For example:

```text
Standard Sales Commission
        │
        ├── Item A → 5%
        ├── Item B → 7%
        └── Customer Group X → 10%
```

When an eligible Sales Invoice is submitted, the engine selects the applicable plan and then evaluates its Commission Rules.

## Best Practices

### Use Meaningful Plan Names

Choose names that clearly describe the purpose of the plan.

Good examples:

```text
Standard Sales Commission
Enterprise Sales Commission
FY 2026-27 Sales Commission
North Region Sales Commission
```

Avoid vague names such as:

```text
Plan 1
Test Plan
Commission
```

### Use Validity Dates for Plan Changes

When a new commission configuration should take effect from a specific date, create a new plan with an appropriate **Valid From** date rather than changing historical commission records.

For example:

```text
Old Plan
Valid From: 2026-01-01

New Plan
Valid From: 2026-10-01
```

This makes the transition between commission configurations explicit.

### Keep Historical Calculations Separate

Do not rely on the current plan configuration to explain past commissions.

The Commission Ledger is the historical source for previously calculated commissions.

## Next Step

After creating a Commission Plan, configure the rules that determine when and how commission is calculated.

Continue with [Commission Rules](commission-rules.md).
