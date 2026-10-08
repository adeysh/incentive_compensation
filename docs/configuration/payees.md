# Configure Commission Payees

This guide explains how to configure Commission Payees in the Incentive Compensation Engine.

A Commission Payee represents the person or partner who receives a commission.

A payee links the commission system to the corresponding ERPNext Sales Person or Sales Partner.

## Before You Begin

Before creating a Commission Payee, make sure the corresponding ERPNext record already exists.

Depending on the type of recipient, you will need either:

- an ERPNext Sales Person
- an ERPNext Sales Partner

You should also understand which sales entity will appear on the relevant ERPNext Sales Invoice.

## Create a Commission Payee

Open:

**Commission Payee → New**

Configure:

| Field         | What to Enter                                                       |
| ------------- | ------------------------------------------------------------------- |
| Payee Name    | A clear name identifying the commission recipient                   |
| Payee Type    | Employee or Sales Partner                                           |
| Sales Person  | ERPNext Sales Person when Payee Type is Employee                    |
| Sales Partner | ERPNext Sales Partner when Payee Type is Sales Partner              |
| Enabled       | Whether the payee should participate in new commission calculations |

The link field shown and required depends on the selected Payee Type.

## Payee Name

Use a clear name that identifies the recipient.

For example:

```text
John Doe Commission
Acme Partner Commission
```

The name is used to identify the payee throughout the commission system.

It does not replace the underlying ERPNext Sales Person or Sales Partner record.

## Payee Type

Select the type of recipient.

Available options are:

```text
Employee
Sales Partner
```

The selected type determines which ERPNext record should be linked.

## Employee Payees

Use **Employee** when the commission recipient is represented through an ERPNext Sales Person.

Configure:

```text
Payee Type: Employee
Sales Person: <ERPNext Sales Person>
```

For example:

| Field        | Example             |
| ------------ | ------------------- |
| Payee Name   | John Doe Commission |
| Payee Type   | Employee            |
| Sales Person | John Doe            |
| Enabled      | Yes                 |

The Sales Person link is used when resolving the commission recipient from the sales transaction.

## Sales Partner Payees

Use **Sales Partner** when the commission recipient is represented through an ERPNext Sales Partner.

Configure:

```text
Payee Type: Sales Partner
Sales Partner: <ERPNext Sales Partner>
```

For example:

| Field         | Example                 |
| ------------- | ----------------------- |
| Payee Name    | Acme Partner Commission |
| Payee Type    | Sales Partner           |
| Sales Partner | Acme Partner            |
| Enabled       | Yes                     |

## Why the Commission Payee Exists

ERPNext already contains Sales Persons and Sales Partners.

The Commission Payee provides a single commission-specific representation of the recipient.

The commission engine can therefore work with:

```text
Commission Payee
      │
      ├── Sales Person
      │
      └── Sales Partner
```

This keeps commission records consistent regardless of which ERPNext entity represents the recipient.

## Payees and Sales Team

For Sales Invoice-based commissions, Sales Team information is important when resolving employee-based commission recipients.

A simplified relationship is:

```text
Sales Invoice
      ↓
Sales Team
      ↓
Sales Person
      ↓
Commission Payee
```

For example:

```text
Sales Invoice
│
└── Sales Team
      │
      └── John Doe → 100%
                    │
                    ▼
             John Doe Commission
```

The transaction builder uses Sales Team contribution when constructing commission calculation inputs.

## Sales Team Contribution

A Sales Invoice can contain one or more Sales Team members.

For example:

```text
Sales Person A → 60%
Sales Person B → 40%
```

The contribution percentages can be used to allocate the applicable commission between the Sales Team members.

For a ₹1,000 commission:

```text
Sales Person A → ₹600
Sales Person B → ₹400
```

The Commission Payee identifies the recipient associated with the relevant Sales Person.

## Enabled Payees

Set:

```text
Enabled: Yes
```

when the payee should participate in new commission calculations.

Disable a payee when they should no longer receive new commissions but their historical commission records should remain available.

For example:

```text
Payee: John Doe Commission
Enabled: No
```

The payee remains in the system for historical reference.

## Choosing the Correct Payee Type

Use **Employee** when the recipient is connected through an ERPNext Sales Person.

Use **Sales Partner** when the recipient is connected through an ERPNext Sales Partner.

The important distinction is:

```text
Payee Type
     ↓
Underlying ERPNext Entity
     ↓
Commission Recipient
```

Choose the type that matches the way the recipient is represented in ERPNext.

## Example: Employee Commission Payee

Suppose an ERPNext Sales Person named `Test Salesperson` participates in sales.

Create:

```text
Payee Name:   Test Salesperson
Payee Type:   Employee
Sales Person: Test Salesperson
Enabled:      Yes
```

On the relevant Sales Invoice, include:

```text
Sales Team
    Test Salesperson → 100%
```

When the invoice is submitted and the commission configuration matches, the commission engine can resolve the Commission Payee associated with that Sales Person.

## Example: Sales Partner Commission Payee

Suppose an external sales partner is represented by an ERPNext Sales Partner.

Create:

```text
Payee Name:    Acme Partner
Payee Type:    Sales Partner
Sales Partner: Acme Partner
Enabled:       Yes
```

The Commission Payee can then represent that partner within the commission system.

## Payees and Commission Ledger

When a commission is calculated, the resolved Commission Payee is stored on the Commission Ledger entry.

For example:

```text
Sales Invoice
      ↓
Commission Calculation
      ↓
Commission Payee: Test Salesperson
      ↓
Commission Ledger
```

This preserves who was identified as the recipient when the commission was calculated.

## Historical Records

Commission Ledger entries retain their Commission Payee.

Changing the current payee configuration does not rewrite historical ledger calculations.

This allows historical commission records to remain traceable to the recipient associated with the calculation.

## Disabling Instead of Deleting

If a recipient should no longer receive new commissions, disable the Commission Payee rather than deleting it unnecessarily.

This preserves the payee record for historical references.

The general approach is:

```text
Active Payee
     ↓
No longer active
     ↓
Enabled = No
```

rather than removing the historical identity from the system.

## Troubleshooting

### The Payee Is Not Being Resolved

For an Employee payee, check:

1. Payee Type is **Employee**.
2. The correct Sales Person is linked.
3. The Commission Payee is Enabled.
4. The Sales Person appears in the Sales Invoice's Sales Team.
5. The Sales Team contribution is configured correctly.
6. The Commission Rule matches the transaction.

For a Sales Partner payee, check:

1. Payee Type is **Sales Partner**.
2. The correct Sales Partner is linked.
3. The Commission Payee is Enabled.
4. The relevant commission configuration is correct.

### The Wrong Person Receives the Commission

Check the Sales Team on the Sales Invoice.

The commission recipient for employee-based sales is resolved through the Sales Person information associated with the transaction.

Make sure the intended Sales Person and Commission Payee relationship is configured correctly.

## Best Practices

### Use One Clear Payee Identity

Give each Commission Payee a name that clearly identifies the recipient.

### Link the Correct ERPNext Record

Make sure the Sales Person or Sales Partner link corresponds to the entity actually used by the sales process.

### Keep Historical Payees

Disable payees that are no longer active instead of deleting them when historical records may depend on them.

### Check Sales Team Configuration

For employee-based commissions, make sure the relevant Sales Person is present in the Sales Invoice's Sales Team.

### Test the Complete Chain

When setting up a new employee payee, verify:

```text
Sales Person
      ↓
Commission Payee
      ↓
Sales Invoice Sales Team
      ↓
Commission Rule
      ↓
Commission Ledger
```

This makes it easier to identify configuration problems before processing real commissions.

## Next Step

Once the Commission Plan, Rules, and Payees are configured, create a Sales Invoice and allow the commission engine to calculate the commission.

For the complete operational process, see [Commission Lifecycle](../workflows/commission-lifecycle.md).
