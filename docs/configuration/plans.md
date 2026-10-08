# Configure Commission Plans

This guide explains how to configure a Commission Plan for the Incentive Compensation Engine.

A Commission Plan defines the overall commission context for a company and provides the plan under which Commission Rules are evaluated.

## Before You Begin

Before creating a Commission Plan, make sure:

- the company exists in ERPNext
- the currency you want to use is available
- you understand the period for which the plan should apply
- you know which commission rules you intend to create under the plan

A plan should normally be configured before creating its Commission Rules.

## Create a Commission Plan

Open:

**Commission Plan → New**

Configure the following fields.

| Field      | What to Enter                                         |
| ---------- | ----------------------------------------------------- |
| Plan Name  | A clear, unique name for the plan                     |
| Company    | The ERPNext Company for which the plan applies        |
| Currency   | Currency used for commission calculations and payouts |
| Valid From | Date from which the plan can apply                    |
| Valid To   | Optional date after which the plan is no longer valid |
| Status     | Draft, Active, Disabled, or Expired                   |

## 1. Plan Name

Give the plan a descriptive name that makes its purpose immediately clear.

Good examples:

```text
Standard Sales Commission
FY 2026-27 Sales Commission
Enterprise Sales Commission
North Region Sales Commission
```

Avoid generic names such as:

```text
Plan 1
Test Plan
Commission
```

A meaningful name makes the plan easier to identify when configuring rules and investigating commission calculations.

## 2. Company

Select the ERPNext Company to which the plan belongs.

For example:

```text
Company: Your Company
```

The commission engine uses the company when determining whether a plan is applicable to a Sales Invoice.

A plan configured for one company should not be expected to apply to transactions belonging to another company.

## 3. Currency

Select the currency used for commission calculations and payouts.

For example:

```text
Currency: INR
```

The currency becomes part of the commission configuration and is also used when matching ledger entries for Commission Statements.

Use the currency appropriate for the company's commission process.

## 4. Valid From

Set the date from which the plan can apply.

For example:

```text
Valid From: 2026-10-01
```

The plan can be considered for eligible transactions occurring on or after its validity start date.

When introducing a new commission configuration, use Valid From to clearly define when the new configuration becomes effective.

## 5. Valid To

Valid To is optional.

For a plan with a defined end date:

```text
Valid From: 2026-10-01
Valid To:   2026-12-31
```

For an open-ended plan:

```text
Valid From: 2026-10-01
Valid To:   —
```

Leaving Valid To empty allows the plan to remain open-ended rather than assigning it a predetermined expiration date.

## 6. Status

Select the appropriate plan status.

Available statuses are:

```text
Draft
Active
Disabled
Expired
```

### Draft

Use Draft while the plan is being configured.

A Draft plan is not an active commission configuration.

### Active

An Active plan is available for commission evaluation when it also satisfies the required company and validity conditions.

Use Active when the plan is ready to process commissions.

### Disabled

Use Disabled when a plan should no longer be used for new commission calculations but should remain available for reference.

### Expired

Expired indicates that the plan's validity period has ended.

## Recommended Setup

For a new plan that should begin on October 1:

| Field      | Example                   |
| ---------- | ------------------------- |
| Plan Name  | Standard Sales Commission |
| Company    | Your Company              |
| Currency   | INR                       |
| Valid From | 2026-10-01                |
| Valid To   | Leave empty               |
| Status     | Active                    |

After saving the plan, create the Commission Rules that belong to it.

## Plan Selection

The commission engine considers active plans that match the Sales Invoice's company and transaction date.

When more than one active plan is valid for the same transaction date, the plan with the most recent Valid From date takes precedence.

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

the newer plan is selected:

```text
Plan B
```

This allows a new plan to take over from an older plan at a defined effective date.

## Replacing an Existing Plan

When introducing a new commission configuration, create a new plan with its own Valid From date rather than modifying historical commission calculations.

For example:

```text
Existing Plan
Valid From: 2026-01-01

New Plan
Valid From: 2026-10-01
```

The newer plan can then take precedence for transactions from October 1 onward.

The Commission Ledger preserves calculations that were already created under the previous configuration.

## Adding Rules

After creating the plan, create the Commission Rules that define the actual commission conditions and calculations.

For example:

```text
Standard Sales Commission
│
├── Smartphone Commission → 5%
├── Laptop Commission     → 7%
└── Enterprise Customers  → 10%
```

The plan provides the configuration context.

The rules determine when and how commission is calculated.

See [Rules](rules.md) for detailed rule configuration.

## Example: Complete Plan Setup

Suppose a company wants to introduce a standard sales commission beginning October 1.

Create:

```text
Plan Name: Standard Sales Commission
Company:    Your Company
Currency:   INR
Valid From: 2026-10-01
Valid To:   —
Status:     Active
```

Then create the associated Commission Rules.

For example:

```text
Standard Sales Commission
        │
        ├── Smartphone → 5%
        ├── Laptop → 7%
        └── Enterprise Customer → 10%
```

The plan and rules together provide the configuration used when eligible Sales Invoices are processed.

## Changing Plan Configuration

Plan configuration can change over time.

When making a change that should affect future transactions, consider whether the change represents a new commission period or configuration.

For a clear configuration transition, use a new Commission Plan with a new Valid From date.

Do not expect changing current configuration to rewrite historical Commission Ledger entries.

Historical ledger entries preserve the commission configuration and calculation values that were recorded when the commission was created.

## Troubleshooting

### The Plan Is Not Being Selected

Check:

1. The plan status is **Active**.
2. The Company matches the Sales Invoice company.
3. The transaction date falls within the plan's validity period.
4. Another active plan with a more recent Valid From date is not taking precedence.

### A Rule Is Not Being Evaluated

First confirm that the correct Commission Plan is being selected.

Then check the Commission Rule configuration, including:

- Commission Plan
- Rule Applies To
- matching condition
- Priority
- Calculation Method
- Enabled status

See [Rules](rules.md) for the rule configuration process.

## Best Practices

### Use One Clear Purpose Per Plan

Name plans according to their business purpose and validity period.

### Define Effective Dates Carefully

Use Valid From and Valid To to make plan changes explicit.

### Keep Historical Configuration Traceable

Use new plans for meaningful configuration changes rather than trying to reinterpret historical commission calculations.

### Activate Only Ready Plans

Keep plans in Draft while configuring them and change them to Active when they are ready to participate in commission processing.

## Next Step

Once the Commission Plan is configured, create the rules that determine which transactions generate commission and how that commission is calculated.

Continue with [Rules](rules.md).
