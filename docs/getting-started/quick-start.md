# Quick Start

This guide walks through a complete commission lifecycle using the Incentive Compensation Engine.

By the end of the guide, you will have:

- configured a Commission Plan
- created a Commission Rule
- configured a Commission Payee
- created an ERPNext Sales Invoice
- generated a Commission Ledger entry automatically
- generated a Commission Statement
- reviewed, approved, and posted the statement
- created a Commission Payout
- processed and paid the payout

## Before You Begin

Make sure the application is installed on your ERPNext site.

You will also need:

- a Company
- a Currency
- an Item
- a Customer
- an ERPNext Sales Person

For this walkthrough, the examples use a percentage-based commission.

## 1. Create a Commission Plan

Open **Commission Plan** and create a new record.

Configure the plan with:

| Field      | Example                   |
| ---------- | ------------------------- |
| Plan Name  | Standard Sales Commission |
| Company    | Your Company              |
| Currency   | INR                       |
| Valid From | Current date              |
| Valid To   | Leave empty               |
| Status     | Active                    |

Save the Commission Plan.

The plan defines the overall configuration and validity period within which commission rules can apply.

## 2. Create a Commission Rule

Open **Commission Rule** and create a new record.

For a simple percentage commission, configure:

| Field              | Example                   |
| ------------------ | ------------------------- |
| Rule Name          | Demo Item Commission      |
| Commission Plan    | Standard Sales Commission |
| Priority           | 1                         |
| Rule Applies To    | Item                      |
| Item               | Your Item                 |
| Calculation Method | Percentage                |
| Rate               | 5                         |
| Enabled            | Yes                       |

Save the Commission Rule.

The rule determines when a commission applies and how the commission amount is calculated.

For example, with a rate of 5%:

```text
Sales Amount = ₹10,000
Commission Rate = 5%

Commission = ₹10,000 × 5%
           = ₹500
```

## 3. Create a Commission Payee

Open **Commission Payee** and create a new record.

For an employee-based commission:

| Field        | Example                    |
| ------------ | -------------------------- |
| Payee Name   | E2E Commission Salesperson |
| Payee Type   | Employee                   |
| Sales Person | Your ERPNext Sales Person  |
| Enabled      | Yes                        |

Save the Commission Payee.

A Commission Payee represents the person or partner who receives the commission. It links the commission system to the corresponding ERPNext Sales Person or Sales Partner.

## 4. Create a Sales Invoice

Create a new ERPNext **Sales Invoice**.

Select:

- your Customer
- your Company
- the Item used by the Commission Rule

Add the Item with a value that will produce a commission.

For example:

| Field    | Example   |
| -------- | --------- |
| Item     | Your Item |
| Quantity | 1         |
| Rate     | ₹10,000   |
| Amount   | ₹10,000   |

In the **Sales Team** section, add the Sales Person linked to your Commission Payee.

Set the Sales Person's contribution to:

```text
100%
```

Submit the Sales Invoice.

## 5. Verify the Commission Ledger

When the Sales Invoice is submitted, the Incentive Compensation Engine evaluates the transaction and creates a Commission Ledger entry when a matching commission configuration is found.

Open **Commission Ledger** and locate the entry generated from your Sales Invoice.

For the example above, you should see values similar to:

| Field              | Example                    |
| ------------------ | -------------------------- |
| Sales Invoice      | Your submitted invoice     |
| Commission Payee   | E2E Commission Salesperson |
| Commission Rule    | Demo Item Commission       |
| Commission Plan    | Standard Sales Commission  |
| Calculation Method | Percentage                 |
| Base Amount        | ₹10,000                    |
| Rate               | 5%                         |
| Commission Amount  | ₹500                       |
| Status             | Calculated                 |

The Commission Ledger is an immutable historical record of the commission calculation.

## 6. Create a Commission Statement

Open **Commission Statement** and create a new record.

Select:

| Field            | Example                    |
| ---------------- | -------------------------- |
| Commission Payee | E2E Commission Salesperson |
| Company          | Your Company               |
| Currency         | INR                        |
| From Date        | Invoice transaction date   |
| To Date          | Invoice transaction date   |

Save the statement.

The newly saved statement remains in **Draft** status.

## 7. Generate the Statement

Open the saved Draft Commission Statement.

Click:

**Generate Statement**

The engine searches for eligible Commission Ledger entries matching the statement's:

- Commission Payee
- Company
- Currency
- date range

Ledger entries that have already been included in another non-cancelled statement are excluded.

After successful generation, the statement contains the commission snapshot.

For the example above:

```text
Gross Commission    ₹500
Adjustments           ₹0
Net Commission      ₹500
```

The statement status becomes:

```text
Generated
```

Once generated, the statement and its ledger entries form an immutable snapshot.

## 8. Submit the Statement for Review

From the Generated statement, click:

**Submit for Review**

The status changes to:

```text
Generated
      ↓
Under Review
```

This represents the review stage of the commission process.

## 9. Approve the Statement

From the Under Review statement, click:

**Approve**

The status changes to:

```text
Under Review
      ↓
Approved
```

The approved statement is ready to be finalized.

## 10. Post the Statement

From the Approved statement, click:

**Post**

The status changes to:

```text
Approved
      ↓
Posted
```

A Posted statement is finalized and can be used to create a Commission Payout.

## 11. Create a Commission Payout

From the Posted Commission Statement, click:

**Create Payout**

The application creates a Commission Payout for the statement's net commission amount.

For the example:

```text
Statement Net Commission = ₹500
Payout Amount            = ₹500
```

The payout starts in:

```text
Pending
```

## 12. Process the Payout

Open the newly created Commission Payout.

Move the payout through its workflow:

```text
Pending
   ↓
Processing
```

When the payment has actually been made, enter the required payment information.

For example:

| Field             | Example                    |
| ----------------- | -------------------------- |
| Payment Date      | Payment date               |
| Payment Reference | Bank transaction reference |

Save the payout.

Then click:

**Mark as Paid**

The payout moves to:

```text
Processing
      ↓
Paid
```

The associated Commission Statement is also marked as **Paid**.

## Complete Lifecycle

You have now completed the full commission lifecycle:

```text
Sales Invoice
      ↓
Commission Calculation
      ↓
Commission Ledger
      ↓
Commission Statement
      ↓
Generated
      ↓
Under Review
      ↓
Approved
      ↓
Posted
      ↓
Commission Payout
      ↓
Processing
      ↓
Paid
```

## What You Learned

The Incentive Compensation Engine separates the commission lifecycle into distinct records:

| Record               | Purpose                                                  |
| -------------------- | -------------------------------------------------------- |
| Commission Plan      | Defines the overall commission plan and validity         |
| Commission Rule      | Defines when and how commission is calculated            |
| Commission Payee     | Identifies who receives the commission                   |
| Commission Ledger    | Records the calculated commission                        |
| Commission Statement | Groups eligible commissions into a period-based snapshot |
| Commission Payout    | Tracks the actual payment of the statement               |

For a deeper explanation of each component, continue to [Concepts](../concepts/overview.md).
