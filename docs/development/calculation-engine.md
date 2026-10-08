# Calculation Engine

The calculation engine is responsible for determining how much commission a transaction should generate.

It separates transaction preparation, configuration resolution, commission evaluation, and mathematical calculation so that each part of the process has a focused responsibility.

## Calculation Flow

The overall calculation pipeline is:

```text
ERPNext Sales Invoice
        ↓
Transaction Builder
        ↓
Plan Resolution
        ↓
Rule Resolution
        ↓
Payee Resolution
        ↓
Commission Evaluation
        ↓
Commission Calculation
        ↓
Commission Ledger
```

The calculation engine does not replace ERPNext's Sales Invoice processing. It consumes the relevant sales transaction information and produces Commission Ledger entries.

## Main Modules

The calculation process is divided across several modules:

| Module                   | Responsibility                                                 |
| ------------------------ | -------------------------------------------------------------- |
| `transaction_builder.py` | Converts Sales Invoice data into commission calculation inputs |
| `resolver.py`            | Resolves plans, rules, tiers, and payees                       |
| `evaluator.py`           | Coordinates resolution and calculation                         |
| `engine.py`              | Applies the selected commission calculation method             |
| `calculator.py`          | Contains the low-level mathematical calculation functions      |
| `ledger.py`              | Persists the calculated result as Commission Ledger entries    |

This separation keeps business rules out of the low-level calculation functions.

## Step 1: Build the Transaction

The calculation process starts with an ERPNext Sales Invoice.

The transaction builder prepares the invoice data for commission evaluation.

For Sales Invoice items, the relevant commission base is derived from the transaction amount.

Sales Team contribution is also considered at this stage.

For example:

```text
Invoice Item Amount = ₹10,000

Sales Person A = 60%
Sales Person B = 40%
```

The transaction builder produces separate allocation inputs:

```text
Sales Person A
Base Amount = ₹6,000

Sales Person B
Base Amount = ₹4,000
```

This allows the same invoice item to produce separate commission calculations for different Sales Team members.

## Sales Team Allocation

ERPNext Sales Invoices can contain one or more Sales Team members.

Each member can have a contribution percentage.

The commission engine uses that contribution to determine the amount on which the member's commission is calculated.

For example:

```text
Invoice Amount = ₹20,000

Sales Person A = 70%
Sales Person B = 30%
```

The allocated bases are:

```text
A = ₹20,000 × 70% = ₹14,000

B = ₹20,000 × 30% = ₹6,000
```

The resulting commission records retain the transaction context needed to understand how the base amount was produced.

## Step 2: Resolve the Commission Plan

After the transaction is prepared, the resolver determines which Commission Plan applies.

The plan must be applicable to the transaction's:

- Company
- transaction date
- active status

The validity period is evaluated using `valid_from` and `valid_to`.

When multiple applicable plans exist, the plan with the most recent `valid_from` is selected.

Conceptually:

```text
Applicable Plans
       │
       ├── Plan A — valid from Jan 1
       ├── Plan B — valid from Apr 1
       └── Plan C — valid from Jul 1
                    ▲
                    │
             selected plan
```

For a transaction in August, Plan C would take precedence if all three plans are otherwise applicable.

This allows newer plans to supersede older plans without modifying historical commission records.

## Step 3: Resolve the Commission Rule

Once the plan is selected, the engine evaluates the Commission Rules belonging to that plan.

A rule can specify what the commission applies to.

Supported rule conditions include:

- Item
- Item Group
- Sales Person
- Customer
- Customer Group
- Territory

The rule also contains the calculation method and its associated configuration.

For example:

```text
Commission Plan
└── Standard Sales Commission
       │
       ├── Rule: Premium Smartphone
       │     Applies to: Item
       │     Item: Smartphone
       │
       └── Rule: Electronics Group
             Applies to: Item Group
             Item Group: Electronics
```

Rules are evaluated according to their priority.

Lower priority numbers are evaluated first when multiple rules match.

## Rule Matching

The resolver checks the condition represented by `based_on` and compares it with the transaction context.

For example, an Item rule can be conceptually evaluated as:

```text
Rule Applies To = Item
Rule Item       = Smartphone

Transaction Item = Smartphone

        ↓

Match
```

A non-matching rule does not produce a commission calculation.

The selected rule supplies the calculation configuration to the evaluator.

## Step 4: Resolve the Commission Payee

The engine determines who should receive the commission from the transaction's Sales Team information and the configured Commission Payee.

A Commission Payee represents the recipient of commission.

The application supports:

- Employee payees
- Sales Partner payees

For an employee-based commission, the payee is linked to the relevant ERPNext Sales Person.

The payee resolution therefore connects:

```text
Sales Invoice
     ↓
Sales Team
     ↓
Sales Person
     ↓
Commission Payee
```

The resolved payee is stored on the resulting Commission Ledger entry.

## Step 5: Determine the Calculation Base

The calculation base is the transaction amount to which the commission method is applied.

For a simple single-person allocation:

```text
Item Amount = ₹10,000
Sales Team Contribution = 100%

Base Amount = ₹10,000
```

For a partial contribution:

```text
Item Amount = ₹10,000
Sales Team Contribution = 50%

Base Amount = ₹5,000
```

The base amount is recorded on the Commission Ledger so that the historical calculation can be understood later.

## Calculation Methods

The engine supports three primary calculation methods:

1. Percentage
2. Fixed Amount
3. Tiered

The selected Commission Rule determines which method is used.

---

## Percentage Calculation

Percentage calculation applies a commission rate to the calculated base amount.

The basic formula is:

```text
Commission = Base Amount × Rate / 100
```

For example:

```text
Base Amount = ₹10,000
Rate = 5%

Commission = ₹10,000 × 5 / 100
           = ₹500
```

The resulting commission amount is stored in the ledger.

### Partial Sales Team Allocation

If the Sales Person receives 60% contribution:

```text
Invoice Amount = ₹10,000
Contribution = 60%

Base Amount = ₹6,000

Rate = 5%

Commission = ₹6,000 × 5 / 100
           = ₹300
```

The commission is therefore based on the Sales Person's allocated transaction value rather than automatically using the full invoice item amount.

---

## Fixed Amount Calculation

A fixed commission does not depend on the percentage of the transaction amount.

Instead, the Commission Rule specifies a fixed commission amount.

Conceptually:

```text
Fixed Commission = Configured Fixed Amount
```

For example:

```text
Fixed Amount = ₹250

Commission = ₹250
```

The fixed amount is stored with the resulting ledger entry.

The base transaction information is still retained so that the commission can be traced back to the source transaction.

---

## Tiered Calculation

Tiered commission applies different rates according to the transaction amount.

A Commission Rule using the Tiered calculation method contains Commission Tier child records.

A tier contains:

- From Amount
- To Amount
- Rate
- Description

A final tier can leave `To Amount` empty, meaning there is no upper limit.

For example:

```text
From       To         Rate
₹0         ₹10,000    2%
₹10,000    ₹20,000    3%
₹20,000    blank      5%
```

The tier configuration determines which rate applies to the calculation.

### Tier Selection

The engine compares the calculation amount with the configured tier ranges.

Conceptually:

```text
Transaction Amount
       │
       ▼
Find matching tier
       │
       ▼
Use tier rate
       │
       ▼
Calculate commission
```

The selected rate is recorded on the resulting Commission Ledger entry.

## Decimal-Based Calculations

Commission calculations use decimal arithmetic rather than relying on binary floating-point arithmetic.

This is important for financial calculations because decimal values need predictable monetary precision.

The calculation layer therefore works with `Decimal` values for commission-related arithmetic.

Conceptually:

```text
Transaction Amount
        ↓
     Decimal
        ↓
Calculation
        ↓
 Commission
```

This helps avoid unexpected floating-point rounding behavior.

## Evaluator Responsibilities

The evaluator acts as the coordinator between transaction data, configuration resolution, and calculation.

Conceptually:

```text
Evaluator
   │
   ├── Resolve Plan
   │
   ├── Resolve Rule
   │
   ├── Resolve Payee
   │
   ├── Determine Base
   │
   └── Calculate Commission
```

The evaluator should not need to implement every mathematical calculation itself.

Instead, it supplies the appropriate inputs to the calculation layer.

## Engine Responsibilities

The engine provides the calculation layer used by the evaluator.

It selects the appropriate calculation behavior based on the Commission Rule's calculation method.

Conceptually:

```text
Calculation Method
       │
       ├── Percentage → percentage calculation
       │
       ├── Fixed      → fixed calculation
       │
       └── Tiered     → tier calculation
```

This keeps method selection separate from the lower-level arithmetic.

## Calculator Responsibilities

The calculator contains the low-level calculation functions.

These functions are intentionally independent of Frappe document operations.

For example, a percentage calculation can conceptually be represented as:

```text
calculate_percentage(base_amount, rate)
        ↓
commission_amount
```

A tiered calculation similarly receives the relevant amount and tier configuration and returns the calculated result.

Keeping these functions focused makes them easier to test independently.

## Calculation Result

After the calculation is complete, the engine has the information required to create a Commission Ledger entry.

A typical result contains information such as:

```text
Sales Invoice
Sales Invoice Item
Commission Payee
Commission Rule
Commission Plan
Calculation Method
Base Amount
Rate
Fixed Amount
Commission Amount
Transaction Date
Company
Currency
```

The ledger layer persists this result.

## Creating the Ledger Entry

The calculation engine does not treat the calculated amount as the final historical record by itself.

The result is passed to the ledger layer.

The ledger layer creates a Commission Ledger entry containing the calculation result and its source context.

Conceptually:

```text
Calculation Result
       │
       ▼
Ledger Creation
       │
       ▼
Commission Ledger
```

Once created, the ledger entry becomes the historical representation of that commission calculation.

## Idempotency

The ledger creation process uses a `source_key`.

The source key identifies the calculation source so that the same commission calculation is not inserted multiple times.

Conceptually:

```text
Sales Invoice Event
       │
       ▼
Calculate Commission
       │
       ▼
Generate Source Key
       │
       ▼
Already Exists?
    /       \
  Yes        No
  │           │
Skip       Create Ledger
```

This protects the system against duplicate commission records when the same processing operation is encountered more than once.

## Historical Snapshot

The calculation engine records the configuration used for the calculation in the ledger.

This is important because Commission Plans and Rules can change over time.

For example:

```text
January
Rule = 5%
Commission = ₹500

        ↓

Rule changed

        ↓

March
Rule = 7%
Commission = ₹700
```

The January ledger entry remains ₹500.

The later rule change does not recalculate the historical January entry.

This makes the ledger an historical snapshot of what the engine calculated at the time of the transaction.

## Reversal Calculations

Cancellation of a source Sales Invoice is handled as a separate ledger operation.

The original commission entry is not edited to change its amount.

Instead, the ledger layer creates a reversal entry.

Conceptually:

```text
Original Commission
₹500
    │
    │ Sales Invoice cancelled
    ▼
Reversal
-₹500
```

The reversal entry references the original commission through `reversal_of`.

This preserves the original calculation while representing the financial effect of the cancellation separately.

## Calculation and Statements

Commission Statements do not recalculate the commission amount.

Instead:

```text
Sales Invoice
     ↓
Calculation Engine
     ↓
Commission Ledger
     ↓
Statement Resolver
     ↓
Commission Statement
```

The statement uses already-calculated ledger entries.

This means that statement generation does not depend on the current Commission Rule configuration.

It uses the historical results stored in the ledger.

## Calculation and Reports

Reports also use the Commission Ledger as their historical source.

```text
Commission Calculation
        ↓
Commission Ledger
        ├──→ Statements
        └──→ Reports
```

This prevents reports from producing different results simply because a Commission Rule has changed since the original transaction.

## Example: Complete Percentage Calculation

Consider a Sales Invoice containing:

```text
Item: Smartphone
Quantity: 1
Rate: ₹10,000
```

The Sales Team contains:

```text
Sales Person: Salesperson A
Contribution: 100%
```

The applicable configuration is:

```text
Plan: Standard Sales Commission

Rule:
  Rule Applies To: Item
  Item: Smartphone
  Calculation Method: Percentage
  Rate: 5%
```

The calculation proceeds as follows.

### 1. Transaction Base

```text
₹10,000 × 100%
= ₹10,000
```

### 2. Commission Rate

```text
5%
```

### 3. Commission

```text
₹10,000 × 5%
= ₹500
```

### 4. Ledger Result

```text
Base Amount       = ₹10,000
Rate              = 5%
Commission Amount = ₹500
```

The result is stored as a Commission Ledger entry.

## Example: Multiple Sales Team Members

Consider:

```text
Invoice Item Amount = ₹20,000
```

Sales Team:

```text
Sales Person A = 70%
Sales Person B = 30%
```

Commission Rule:

```text
Rate = 5%
```

The engine processes the allocations independently.

For A:

```text
Base = ₹20,000 × 70%
     = ₹14,000

Commission = ₹14,000 × 5%
           = ₹700
```

For B:

```text
Base = ₹20,000 × 30%
     = ₹6,000

Commission = ₹6,000 × 5%
           = ₹300
```

The resulting commission records are:

```text
Sales Person A → ₹700
Sales Person B → ₹300
```

The total commission is:

```text
₹700 + ₹300 = ₹1,000
```

## Testing the Calculation Layer

The low-level calculation functions are suitable for isolated tests because they do not need to perform Frappe document operations.

Calculation tests should cover:

- percentage calculations
- fixed amount calculations
- tiered calculations
- tier boundaries
- open-ended final tiers
- sales team allocation
- decimal arithmetic
- expected commission results

Higher-level tests can then verify that the resolved configuration is correctly connected to the calculator and ledger.

## Debugging a Calculation

When a commission result is unexpected, inspect the calculation in this order:

```text
1. Sales Invoice
       ↓
2. Sales Team contribution
       ↓
3. Commission Plan
       ↓
4. Commission Rule
       ↓
5. Commission Payee
       ↓
6. Base Amount
       ↓
7. Calculation Method
       ↓
8. Rate / Fixed Amount / Tiers
       ↓
9. Commission Ledger
```

This mirrors the actual processing pipeline and makes it easier to identify where an unexpected result originated.

## Design Principles

The calculation engine follows several principles:

### Resolve before calculating

The system first determines the applicable plan, rule, and payee before performing the mathematical calculation.

### Keep mathematics isolated

Low-level calculation functions should not need to know about Frappe documents, workflows, or database operations.

### Preserve transaction context

The calculation result retains enough information to understand where the commission came from.

### Use Decimal arithmetic

Financial calculations use decimal arithmetic for predictable monetary behavior.

### Make calculations reproducible

The ledger stores the historical calculation result so later configuration changes do not alter historical commissions.

### Separate calculation from lifecycle processing

Calculation determines the commission amount. Statements, approvals, and payouts handle what happens to that commission afterward.

## Development Entry Points

When working on the calculation engine, these are the most useful files to inspect:

| File                                       | Start Here When                                          |
| ------------------------------------------ | -------------------------------------------------------- |
| `commission_engine/transaction_builder.py` | Investigating transaction and Sales Team allocation      |
| `commission_engine/resolver.py`            | Investigating plan, rule, tier, or payee resolution      |
| `commission_engine/evaluator.py`           | Investigating the overall calculation flow               |
| `commission_engine/engine.py`              | Investigating calculation-method dispatch                |
| `commission_engine/calculator.py`          | Investigating mathematical calculation behavior          |
| `commission_engine/ledger.py`              | Investigating ledger creation, idempotency, or reversals |

## Next Step

Continue with [Events](events.md) to understand how ERPNext Sales Invoice submission and cancellation trigger the commission engine.
