# Configure Commission Rules

This guide explains how to configure Commission Rules in the Incentive Compensation Engine.

A Commission Rule defines:

- what a commission applies to
- which value must match for the rule to apply
- how the commission is calculated
- which rule takes precedence when multiple rules match

Commission Rules belong to a Commission Plan.

## Before You Begin

Before creating a Commission Rule, make sure:

- the Commission Plan exists
- the Commission Plan is configured for the correct Company and Currency
- you know what transaction condition should trigger the commission
- you know which calculation method should be used

The Commission Plan provides the context in which the rule is evaluated.

## Create a Commission Rule

Open:

**Commission Rule → New**

Configure the rule using the following fields.

| Field              | What to Enter                                                  |
| ------------------ | -------------------------------------------------------------- |
| Rule Name          | A clear, unique name for the rule                              |
| Commission Plan    | The Commission Plan under which the rule applies               |
| Priority           | The precedence of the rule when multiple rules match           |
| Rule Applies To    | The transaction attribute used for matching                    |
| Item               | Item to match when Rule Applies To is Item                     |
| Item Group         | Item Group to match when Rule Applies To is Item Group         |
| Sales Person       | Sales Person to match when Rule Applies To is Sales Person     |
| Customer           | Customer to match when Rule Applies To is Customer             |
| Customer Group     | Customer Group to match when Rule Applies To is Customer Group |
| Territory          | Territory to match when Rule Applies To is Territory           |
| Calculation Method | Percentage, Fixed Amount, or Tiered                            |
| Rate               | Percentage used by the Percentage method                       |
| Fixed Amount       | Fixed commission amount used by the Fixed Amount method        |
| Tiers              | Commission tiers used by the Tiered method                     |
| Enabled            | Whether the rule is active                                     |

Only the condition relevant to **Rule Applies To** should be configured.

## 1. Rule Name

Give the rule a descriptive name.

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

A meaningful name makes the rule easier to identify during configuration and commission investigation.

## 2. Commission Plan

Select the Commission Plan to which the rule belongs.

For example:

```text
Commission Plan: Standard Sales Commission
```

The rule is evaluated within this plan's context.

The plan determines which commission configuration applies to the transaction, while the rule determines the matching condition and calculation.

## 3. Priority

Set the rule's priority.

Lower priority numbers are evaluated first when multiple rules match.

For example:

```text
Rule A → Priority 1
Rule B → Priority 5
Rule C → Priority 10
```

If all three rules match a transaction, Rule A has the highest precedence.

### Recommended Priority Pattern

Leave gaps between priority values when practical:

```text
1
10
20
30
```

This makes it easier to insert another rule later without renumbering every existing rule.

For example:

```text
Priority 1  → Specific Item
Priority 10 → Item Group
Priority 20 → Territory
```

## 4. Rule Applies To

The **Rule Applies To** field determines which transaction attribute the rule uses for matching.

Available options are:

```text
Item
Item Group
Sales Person
Customer
Customer Group
Territory
```

Choose the option that best represents the business condition for the commission.

### Item

Use **Item** when the rule should apply to a specific item.

Example:

```text
Rule Applies To: Item
Item: Smartphone
```

### Item Group

Use **Item Group** when the rule should apply to items belonging to a particular group.

Example:

```text
Rule Applies To: Item Group
Item Group: Electronics
```

### Sales Person

Use **Sales Person** when the rule should apply to a specific Sales Person.

Example:

```text
Rule Applies To: Sales Person
Sales Person: John Doe
```

### Customer

Use **Customer** when the rule should apply to a specific customer.

Example:

```text
Rule Applies To: Customer
Customer: ABC Industries
```

### Customer Group

Use **Customer Group** when the rule should apply to a category of customers.

Example:

```text
Rule Applies To: Customer Group
Customer Group: Enterprise
```

### Territory

Use **Territory** when the rule should apply to sales associated with a particular territory.

Example:

```text
Rule Applies To: Territory
Territory: North
```

## Matching Conditions

Once Rule Applies To is selected, configure the corresponding condition field.

For example:

```text
Rule Applies To: Item
Item: Smartphone
```

The rule then targets that Item.

Similarly:

```text
Rule Applies To: Customer Group
Customer Group: Enterprise
```

targets the Enterprise Customer Group.

The other condition fields are not relevant to the selected matching dimension.

## 5. Calculation Method

Choose how the commission should be calculated.

The available methods are:

```text
Percentage
Fixed Amount
Tiered
```

The fields required for the calculation depend on this selection.

## Percentage Commission

Select:

```text
Calculation Method: Percentage
```

Then enter the commission rate.

For example:

```text
Rate: 5
```

For a base amount of ₹10,000:

```text
Base Amount = ₹10,000
Rate        = 5%

Commission  = ₹10,000 × 5%
            = ₹500
```

### Configuration Example

```text
Calculation Method: Percentage
Rate: 5
```

Use Percentage when the commission should scale with the applicable transaction amount.

## Fixed Amount Commission

Select:

```text
Calculation Method: Fixed Amount
```

Then enter the fixed commission amount.

For example:

```text
Fixed Amount: ₹500
```

When the rule matches, the configured fixed amount is used for the commission calculation.

### Configuration Example

```text
Calculation Method: Fixed Amount
Fixed Amount: 500
```

Use Fixed Amount when each matching commission event should produce a fixed commission value rather than a percentage of the transaction amount.

## Tiered Commission

Select:

```text
Calculation Method: Tiered
```

Then configure the Commission Tiers.

A tier contains:

- From Amount
- To Amount
- Rate
- Description

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

Leave **To Amount** empty on the final tier when there is no upper limit.

### Tier Configuration

A simple tiered configuration might look like:

| From Amount | To Amount | Rate |
| ----------: | --------: | ---: |
|          ₹0 |   ₹10,000 |   2% |
|     ₹10,000 |   ₹50,000 |   5% |
|     ₹50,000 |     Empty |   8% |

The calculation engine uses the configured tiers when calculating a Tiered commission.

## Calculation Fields

The form shows the fields relevant to the selected Calculation Method.

### Percentage

Configure:

```text
Rate
```

### Fixed Amount

Configure:

```text
Fixed Amount
```

### Tiered

Configure:

```text
Tiers
```

This keeps the rule configuration focused on the calculation method being used.

## 6. Enabled

Set:

```text
Enabled: Yes
```

when the rule should participate in commission calculations.

Disable a rule when it should no longer be used for new calculations but should remain available for reference.

For example:

```text
Rule: Enterprise Customer Commission
Enabled: No
```

The rule remains stored but is not used as an active commission rule.

## Example: Item Percentage Rule

Suppose a company wants to pay 5% commission on Smartphone sales.

Configure:

| Field              | Value                     |
| ------------------ | ------------------------- |
| Rule Name          | Smartphone Commission     |
| Commission Plan    | Standard Sales Commission |
| Priority           | 1                         |
| Rule Applies To    | Item                      |
| Item               | Smartphone                |
| Calculation Method | Percentage                |
| Rate               | 5                         |
| Enabled            | Yes                       |

A ₹10,000 eligible sale produces:

```text
₹10,000 × 5% = ₹500
```

The result is stored in the Commission Ledger.

## Example: Item Group Rule

Suppose the company wants to pay 3% commission on all Electronics items.

Configure:

| Field              | Value                     |
| ------------------ | ------------------------- |
| Rule Name          | Electronics Commission    |
| Commission Plan    | Standard Sales Commission |
| Priority           | 10                        |
| Rule Applies To    | Item Group                |
| Item Group         | Electronics               |
| Calculation Method | Percentage                |
| Rate               | 3                         |
| Enabled            | Yes                       |

The rule can then apply to eligible items within the selected Item Group.

## Example: Customer Rule

Suppose a company wants to pay 10% commission on sales to a specific customer.

Configure:

| Field              | Value                     |
| ------------------ | ------------------------- |
| Rule Name          | ABC Industries Commission |
| Commission Plan    | Standard Sales Commission |
| Priority           | 1                         |
| Rule Applies To    | Customer                  |
| Customer           | ABC Industries            |
| Calculation Method | Percentage                |
| Rate               | 10                        |
| Enabled            | Yes                       |

This makes the customer the matching dimension for the rule.

## Example: Fixed Amount Rule

Suppose every matching transaction should generate a fixed ₹500 commission.

Configure:

| Field              | Value                     |
| ------------------ | ------------------------- |
| Rule Name          | Fixed Sales Commission    |
| Commission Plan    | Standard Sales Commission |
| Priority           | 1                         |
| Rule Applies To    | Item                      |
| Item               | Smartphone                |
| Calculation Method | Fixed Amount              |
| Fixed Amount       | ₹500                      |
| Enabled            | Yes                       |

The commission amount is the configured fixed amount when the rule matches.

## Example: Tiered Rule

Suppose commission rates should increase as the applicable amount increases.

Configure:

| From Amount | To Amount | Rate |
| ----------: | --------: | ---: |
|          ₹0 |   ₹10,000 |   2% |
|     ₹10,000 |   ₹50,000 |   5% |
|     ₹50,000 |     Empty |   8% |

The rule configuration becomes:

```text
Calculation Method: Tiered
```

with the tiers configured in the Tiers table.

## Overlapping Rules

More than one Commission Rule can potentially match the same transaction.

For example:

```text
Rule A
Rule Applies To: Item
Item: Smartphone
Priority: 1
Rate: 5%

Rule B
Rule Applies To: Item Group
Item Group: Electronics
Priority: 10
Rate: 3%
```

If Smartphone belongs to the Electronics Item Group, both rules may match.

Priority determines which matching rule takes precedence.

In this example:

```text
Priority 1
    ↓
Rule A selected
```

The 5% rule therefore takes precedence over the 3% rule.

## Rule Evaluation

When an eligible Sales Invoice is submitted, the commission engine evaluates the applicable plan and its rules.

The process can be summarized as:

```text
Sales Invoice
      ↓
Find Applicable Commission Plan
      ↓
Find Enabled Matching Rules
      ↓
Evaluate Priority
      ↓
Select Applicable Rule
      ↓
Calculate Commission
      ↓
Create Commission Ledger Entry
```

The rule is therefore responsible for both matching and calculation, while the Commission Plan establishes the overall configuration context.

## Changing a Rule

Commission Rule configuration can change over time.

Changing a rule does not modify existing Commission Ledger entries.

For example, a rule may change from:

```text
Rate: 5%
```

to:

```text
Rate: 7%
```

A commission already recorded at 5% remains recorded at 5%.

The updated rule applies to future eligible calculations.

## Troubleshooting

### The Rule Is Not Matching

Check:

1. The Commission Plan is correct.
2. The plan is Active and valid for the transaction date.
3. The rule is Enabled.
4. Rule Applies To is correct.
5. The selected condition matches the Sales Invoice.
6. Another rule with a higher priority is taking precedence.

### The Wrong Rule Is Selected

Check the Priority values of all matching rules.

Remember:

```text
Lower number = Higher precedence
```

For example:

```text
Priority 1  → evaluated before Priority 10
```

### The Commission Amount Is Unexpected

Check the Calculation Method.

For Percentage:

```text
Rate
```

For Fixed Amount:

```text
Fixed Amount
```

For Tiered:

```text
Tiers
```

Also verify the transaction amount being used as the commission base.

## Best Practices

### Make Rules Specific

When a rule is intended for a specific item, customer, or other dimension, configure that condition explicitly.

### Use Priority Deliberately

Use lower priority numbers for rules that should take precedence when multiple rules can match.

### Disable Unused Rules

Disable rules that should no longer participate in new calculations instead of deleting them unnecessarily.

### Keep Rule Names Descriptive

A reviewer should be able to understand the rule's purpose from its name.

### Test Overlapping Rules

When creating rules that could overlap, test a representative Sales Invoice to confirm that the intended rule is selected.

## Next Step

Once Plans and Rules are configured, configure the people or partners who receive commissions.

Continue with [Payees](payees.md).
