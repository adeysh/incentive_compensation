# Commission Payees

A Commission Payee represents the person or partner who receives a commission.

The Commission Payee provides a consistent commission-level identity for the recipient while linking that recipient to the corresponding ERPNext record.

A payee can represent either:

- an ERPNext Sales Person
- an ERPNext Sales Partner

## Why Commission Payees Exist

ERPNext already contains Sales Persons and Sales Partners, so the Commission Payee may initially seem like an extra layer.

The purpose of the Commission Payee is to give the commission engine a single concept for the **recipient of a commission**.

Instead of making every part of the commission system understand different recipient types, the engine works with:

```text
Commission Payee
      │
      ├── Employee / Sales Person
      │
      └── Sales Partner
```

This keeps commission records consistent while still allowing the recipient to originate from different ERPNext entities.

## Fields

| Field         | Description                                                                |
| ------------- | -------------------------------------------------------------------------- |
| Payee Name    | Name used to identify the commission recipient                             |
| Payee Type    | Determines whether the payee represents an Employee or Sales Partner       |
| Sales Person  | ERPNext Sales Person linked to the payee when Payee Type is Employee       |
| Sales Partner | ERPNext Sales Partner linked to the payee when Payee Type is Sales Partner |
| Enabled       | Determines whether the payee can receive new commissions                   |

The relevant link field depends on the selected **Payee Type**.

## Payee Type

The **Payee Type** determines what kind of ERPNext entity receives the commission.

### Employee

Select **Employee** when the commission recipient is represented through an ERPNext Sales Person.

Configure:

```text
Payee Type: Employee
Sales Person: <ERPNext Sales Person>
```

The Sales Person is the ERPNext sales entity used when the commission engine processes the Sales Invoice.

### Sales Partner

Select **Sales Partner** when the commission recipient is an external or partner-based sales entity represented by an ERPNext Sales Partner.

Configure:

```text
Payee Type: Sales Partner
Sales Partner: <ERPNext Sales Partner>
```

## Creating a Commission Payee

Open **Commission Payee** and create a new record.

For an employee-based commission:

| Field        | Example                    |
| ------------ | -------------------------- |
| Payee Name   | E2E Commission Salesperson |
| Payee Type   | Employee                   |
| Sales Person | Your ERPNext Sales Person  |
| Enabled      | Yes                        |

Save the record.

The payee can then be used by the commission engine when resolving the recipient of a commission.

## Payee and Sales Team

For Sales Invoice-based commissions, the Sales Person associated with a Commission Payee is important because the invoice's Sales Team identifies the sales contribution.

For example:

```text
Sales Invoice
      │
      └── Sales Team
             │
             └── Sales Person
                    │
                    ▼
             Commission Payee
```

The transaction builder uses the Sales Team information to determine the sales person's contribution to the invoice.

For example, if one Sales Person has:

```text
Contribution: 100%
```

the commission calculation uses that full contribution.

With multiple Sales Team members, their contribution percentages can be used to allocate the applicable commission between them.

## Enabled Payees

A Commission Payee can be enabled or disabled.

An enabled payee can participate in new commission calculations.

A disabled payee remains in the system for historical reference but should not be used as an active commission recipient.

This allows an organization to retain historical commission records without deleting the payee configuration.

## Historical Commission Records

Commission Ledger entries store the Commission Payee that was resolved when the commission was calculated.

This means historical ledger entries retain their commission recipient even if the current configuration changes later.

The ledger is therefore the historical record of what was calculated and for whom.

## Example

Suppose an ERPNext Sales Person named `John Doe` is responsible for sales.

Create:

```text
Payee Name: John Doe Commission
Payee Type: Employee
Sales Person: John Doe
Enabled: Yes
```

When a matching Sales Invoice is submitted:

```text
Sales Invoice
      ↓
Sales Team → John Doe
      ↓
Commission Payee → John Doe Commission
      ↓
Commission Calculation
      ↓
Commission Ledger
```

The resulting ledger entry records the Commission Payee associated with the calculated commission.

## Choosing the Right Payee Type

Use **Employee** when the recipient is represented through an ERPNext Sales Person.

Use **Sales Partner** when the recipient is represented through an ERPNext Sales Partner.

The important point is that the Commission Payee is the commission system's representation of the recipient, while the linked ERPNext record identifies the underlying sales entity.

## Best Practices

### Use Clear Payee Names

Choose names that make the recipient immediately identifiable.

For example:

```text
John Doe Commission
Acme Partner Commission
North Region Sales Team
```

### Keep Payees Enabled Only While Active

Disable payees that should no longer participate in new commission calculations rather than deleting them.

This helps preserve historical references.

### Link the Correct Sales Person

For employee-based commissions, make sure the Sales Person linked to the Commission Payee is the same Sales Person used in the relevant ERPNext Sales Team records.

An incorrect link can prevent the commission engine from resolving the intended payee.

## Next Step

Once Plans, Rules, and Payees are configured, the commission engine can calculate commissions from eligible ERPNext Sales Invoices.

The result is stored in the immutable Commission Ledger.

Continue with [Commission Ledger](commission-ledger.md).
