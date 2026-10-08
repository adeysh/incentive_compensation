# Commission Rules

A Commission Rule defines **when a commission applies and how the commission is calculated**.

Rules belong to a Commission Plan. When an eligible ERPNext Sales Invoice is processed, the commission engine evaluates the rules in the applicable plan and selects the rule that matches the transaction.

## Purpose

A Commission Rule answers two questions:

1. **Which transactions should this rule apply to?**
2. **How much commission should those transactions generate?**

A rule combines matching conditions with a calculation method.

```text
Commission Plan
       │
       ├── Commission Rule
       │       │
       │       ├── Matching Conditions
       │       │
       │       └── Calculation Method
       │
       └── Commission Rule
```

## Fields

| Field              | Description                                                                     |
| ------------------ | ------------------------------------------------------------------------------- |
| Rule Name          | Unique name identifying the rule                                                |
| Commission Plan    | Commission Plan to which the rule belongs                                       |
| Priority           | Determines which matching rule takes precedence                                 |
| Rule Applies To    | Determines the transaction attribute used for matching                          |
| Item               | Item to which the rule applies when Rule Applies To is Item                     |
| Item Group         | Item Group to which the rule applies when Rule Applies To is Item Group         |
| Sales Person       | Sales Person to whom the rule applies when Rule Applies To is Sales Person      |
| Customer           | Customer to whom the rule applies when Rule Applies To is Customer              |
| Customer Group     | Customer Group to which the rule applies when Rule Applies To is Customer Group |
| Territory          | Territory to which the rule applies when Rule Applies To is Territory           |
| Calculation Method | Determines how commission is calculated                                         |
| Fixed Amount       | Commission amount used with the Fixed Amount method                             |
| Rate               | Commission percentage used with the Percentage method                           |
| Tiers              | Tier definitions used with the Tiered method                                    |
| Enabled            | Determines whether the rule can be used                                         |

Only the condition field relevant to **Rule Applies To** is used for matching.

## Rule Applies To

The **Rule Applies To** field determines what the rule is looking at when it evaluates a transaction.

Available options are:

- Item
- Item Group
- Sales Person
- Customer
- Customer Group
- Territory

For example, an Item-based rule can target a specific product:

```text
Rule Applies To: Item
Item: Smartphone
```

The rule can then match Sales Invoice items containing that Item.

Similarly, a Customer Group rule can target a group of customers:

```text
Rule Applies To: Customer Group
Customer Group: Enterprise
```

The important distinction is that **Rule Applies To defines the matching dimension**, while the selected value defines the specific condition.

## Matching Conditions

A rule can be configured against different ERPNext sales dimensions.

### Item

Use Item when the commission should apply to a specific product.

```text
Rule Applies To: Item
Item: Smartphone
```

### Item Group

Use Item Group when the commission should apply to products belonging to a particular group.

```text
Rule Applies To: Item Group
Item Group: Electronics
```

### Sales Person

Use Sales Person when the commission should apply to a specific salesperson.

```text
Rule Applies To: Sales Person
Sales Person: John Doe
```

### Customer

Use Customer when the commission should apply to a specific customer.

```text
Rule Applies To: Customer
Customer: ABC Industries
```

### Customer Group

Use Customer Group when the commission should apply to a category of customers.

```text
Rule Applies To: Customer Group
Customer Group: Enterprise
```

### Territory

Use Territory when the commission should apply to sales from a particular territory.

```text
Rule Applies To: Territory
Territory: North
```

## Calculation Methods

A Commission Rule supports three calculation methods.

### Percentage

Percentage commission calculates commission as a percentage of the applicable base amount.

For example:

```text
Base Amount = ₹10,000
Rate        = 5%

Commission = ₹10,000 × 5%
           = ₹500
```

Configure the rule with:

```text
Calculation Method: Percentage
Rate: 5
```

### Fixed Amount

Fixed Amount assigns a fixed commission value.

For example:

```text
Calculation Method: Fixed Amount
Fixed Amount: ₹500
```

If the rule matches, the commission amount is ₹500.

### Tiered

Tiered commission uses Commission Tiers to determine the applicable rate based on the transaction amount.

A tier can define:

- From Amount
- To Amount
- Rate
- Description

For example:

```text
From        To          Rate
₹0          ₹10,000     2%
₹10,000     ₹50,000     5%
₹50,000     —           8%
```

The final tier can have an empty **To Amount**, meaning there is no upper limit.

See the tier section below for more detail.

## Commission Tiers

When the calculation method is **Tiered**, the rule uses its Commission Tiers to determine the commission rate.

A tier contains:

| Field       | Description                      |
| ----------- | -------------------------------- |
| From Amount | Lower boundary of the tier       |
| To Amount   | Optional upper boundary          |
| Rate        | Commission rate for the tier     |
| Description | Optional explanation of the tier |

For example:

```text
Tier 1
From: ₹0
To: ₹10,000
Rate: 2%

Tier 2
From: ₹10,000
To: ₹50,000
Rate: 5%

Tier 3
From: ₹50,000
To: —
Rate: 8%
```

A blank **To Amount** means the tier has no upper limit.

The exact tier calculation behavior is handled by the commission calculation engine.

## Priority

Multiple rules can potentially match the same transaction.

The **Priority** field determines which matching rule takes precedence.

Lower priority numbers are evaluated first.

For example:

```text
Rule A → Priority 1
Rule B → Priority 5
Rule C → Priority 10
```

If multiple rules match the transaction, Rule A has the highest precedence because it has the lowest priority number.

This allows more specific or important rules to take precedence over other matching rules.

## Enabled Rules

Only enabled rules are considered during commission evaluation.

This allows a rule to be temporarily disabled without deleting its configuration.

For example:

```text
Rule: Enterprise Customer Commission
Enabled: No
```

The rule remains available for reference but will not be used for new commission calculations.

## Rule Evaluation

When a Sales Invoice is submitted, the commission engine evaluates the applicable Commission Plan and its rules.

Conceptually, the process is:

```text
Sales Invoice
      ↓
Find applicable Commission Plan
      ↓
Find enabled matching Commission Rules
      ↓
Evaluate rule priority
      ↓
Select applicable Rule
      ↓
Calculate Commission
      ↓
Create Commission Ledger Entry
```

The rule does not operate independently of the plan. The plan establishes the configuration context first, and rules are evaluated within that plan.

## Example

Suppose a company has the following plan:

```text
Commission Plan:
Standard Sales Commission
```

It contains these rules:

```text
Priority 1
Rule Applies To: Item
Item: Smartphone
Calculation Method: Percentage
Rate: 5%

Priority 10
Rule Applies To: Item Group
Item Group: Electronics
Calculation Method: Percentage
Rate: 2%
```

A Sales Invoice contains a Smartphone belonging to the Electronics Item Group.

Both rules may match the transaction.

Because the Smartphone rule has priority `1` and the Electronics rule has priority `10`, the Smartphone rule takes precedence.

The resulting commission is therefore calculated using the 5% rule.

## Configuration Example

A simple percentage rule can be configured as:

| Field              | Value                     |
| ------------------ | ------------------------- |
| Rule Name          | Demo Item Commission      |
| Commission Plan    | Standard Sales Commission |
| Priority           | 1                         |
| Rule Applies To    | Item                      |
| Item               | Smartphone                |
| Calculation Method | Percentage                |
| Rate               | 5                         |
| Enabled            | Yes                       |

With a Sales Invoice item worth ₹10,000:

```text
Base Amount = ₹10,000
Rate        = 5%

Commission  = ₹500
```

The resulting calculation is recorded in the Commission Ledger.

## Rule Changes and Historical Data

Changing a Commission Rule does not modify previously calculated Commission Ledger entries.

For example, suppose a rule changes from:

```text
Rate: 5%
```

to:

```text
Rate: 7%
```

A commission that was already calculated at 5% remains recorded at 5%.

The new rule configuration is used for future eligible calculations.

This separation ensures that historical commissions remain auditable.

## Best Practices

### Give Rules Descriptive Names

Use names that describe the condition and calculation.

Good examples:

```text
Smartphone Commission
Enterprise Customer Commission
North Territory Commission
Electronics Item Group Commission
```

Avoid vague names such as:

```text
Rule 1
Test Rule
Commission Rule
```

### Use Priority Deliberately

When rules can overlap, decide which rule should take precedence and give it the appropriate priority.

For example:

```text
Priority 1  → Specific Item
Priority 10 → Item Group
```

This makes the intended precedence clear.

### Disable Instead of Deleting

If a rule should no longer be used, disabling it preserves the configuration for reference while preventing it from being used for new calculations.

## Next Step

After configuring Commission Rules, configure the people or partners who receive the calculated commissions.

Continue with [Commission Payees](commission-payees.md).
