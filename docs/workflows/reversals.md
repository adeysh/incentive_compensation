# Reversals

A commission reversal records the effect of cancelling a Sales Invoice that previously generated commission.

The Incentive Compensation Engine does not modify the original Commission Ledger entry when the source Sales Invoice is cancelled.

Instead, it creates a separate reversal ledger entry.

This preserves the original commission calculation while recording the financial effect of the cancellation.

## Why Reversals Exist

Consider a Sales Invoice that generates:

```text
Commission = ₹500
```

The original commission is recorded in the Commission Ledger.

If the Sales Invoice is later cancelled, the system needs to reflect that the ₹500 commission is no longer valid.

Rather than changing the original entry, the system creates:

```text
Original Commission → +₹500
Reversal            → -₹500
```

The net effect is:

```text
₹500 + (-₹500) = ₹0
```

The original calculation remains visible in the audit trail.

## Reversal Lifecycle

The basic process is:

```text
Sales Invoice Submitted
        ↓
Commission Calculated
        ↓
Commission Ledger
        ↓
Sales Invoice Cancelled
        ↓
Reversal Ledger Entry
```

The reversal is automatically generated when the source Sales Invoice is cancelled.

## Original Commission Entry

When the Sales Invoice is originally submitted and matches the commission configuration, the application creates a normal Commission Ledger entry.

For example:

```text
Entry Type:          Commission
Sales Invoice:       ACC-SINV-2026-00021
Commission Amount:   ₹500
Status:              Calculated
```

This entry represents the commission that was calculated from the original transaction.

## Cancelling the Sales Invoice

When the Sales Invoice is cancelled, the commission event handler triggers commission reversal processing.

The application identifies the commission entries associated with the source invoice and creates corresponding reversal entries.

Conceptually:

```text
Sales Invoice
      │
      ├── Original Commission → +₹500
      │
      └── Cancellation
               │
               ▼
          Reversal → -₹500
```

The original ledger entry is not overwritten.

## Reversal Ledger Entry

A reversal is stored as a separate Commission Ledger entry.

Important fields include:

```text
Entry Type:        Reversal
Commission Amount: Negative original amount
Reversal Of:       Original ledger entry
Sales Invoice:     Original invoice
```

For example:

```text
Original Entry

CL-2026-00001
Entry Type:          Commission
Commission Amount:   ₹500
```

After cancellation:

```text
Reversal Entry

CL-2026-00002
Entry Type:          Reversal
Commission Amount:   -₹500
Reversal Of:         CL-2026-00001
```

This creates an explicit relationship between the original commission and its reversal.

## Why the Original Entry Is Preserved

The original commission entry answers:

> What commission was calculated when the Sales Invoice was submitted?

The reversal answers:

> What happened to that commission when the Sales Invoice was cancelled?

Keeping both entries provides a complete historical record.

If the original entry were simply edited or deleted, the system would lose information about the commission that was originally calculated.

The ledger therefore behaves like an event history:

```text
Original Event
      +
Reversal Event
      =
Complete History
```

## Reversal Amount

The reversal amount is the negative of the original commission amount.

For example:

```text
Original Commission: ₹1,000
Reversal:            -₹1,000
```

The combined effect is:

```text
₹1,000 + (-₹1,000) = ₹0
```

For a normal positive commission, the reversal therefore offsets the original commission.

## Source Key and Duplicate Prevention

Reversal entries also use the Commission Ledger's source-key mechanism.

The reversal source key identifies the source transaction, item, payee, rule, and reversal context.

Conceptually:

```text
Sales Invoice
      +
Sales Invoice Item
      +
Commission Payee
      +
Commission Rule
      +
REVERSAL
      ↓
Reversal Source Key
```

This prevents the same cancellation event from creating duplicate reversal entries if the reversal processing is triggered more than once.

The source key makes reversal processing idempotent.

## Multiple Sales Invoice Items

A Sales Invoice can contain multiple items and therefore multiple commission ledger entries.

When the invoice is cancelled, the application reverses the relevant commission entries individually.

For example:

```text
Invoice
│
├── Item A → Commission +₹500
└── Item B → Commission +₹300
```

After cancellation:

```text
Original Entries
│
├── Item A → +₹500
└── Item B → +₹300

Reversals
│
├── Item A → -₹500
└── Item B → -₹300
```

The total historical effect becomes:

```text
+₹800 + (-₹800) = ₹0
```

The item-level relationship remains traceable.

## Reversals and Immutability

The reversal process follows the same immutability principle as normal Commission Ledger entries.

The original entry is not edited.

The reversal is created as a new historical record.

Both entries are preserved.

```text
Original Ledger Entry
        │
        │ immutable
        ▼
Reversal Ledger Entry
        │
        │ immutable
        ▼
Historical Audit Trail
```

This means the ledger can be examined later to understand both the original calculation and the subsequent cancellation.

## Reversals and Commission Statements

Commission Statements use Commission Ledger entries as their source data.

This means reversal entries can affect the commission represented by ledger data.

For example:

```text
Original Commission → +₹500
Reversal            → -₹500
```

Together they represent no remaining commission effect from the cancelled transaction.

A statement generated from eligible ledger entries therefore reflects the ledger history available for its selected payee, company, currency, and date range.

## Important Timing Consideration

A reversal is generated when the Sales Invoice is cancelled.

Therefore, whether a reversal appears in a particular Commission Statement depends on the statement's date range and the eligibility rules used when the statement is generated.

The reversal is a separate ledger event with its own calculation date while retaining the source transaction reference.

When investigating a statement, inspect the underlying Commission Ledger entries to determine whether an original commission or reversal is included.

## Reversal After a Statement Exists

A Sales Invoice can potentially be cancelled after its commission has already been included in a Commission Statement.

In that situation, the original statement remains a historical snapshot.

The newly created reversal is a separate Commission Ledger event.

The system does not rewrite the previously generated statement to silently change its historical contents.

The reversal can therefore be handled through subsequent commission processing according to the organization's workflow.

## Example

Suppose a salesperson generates a commission:

```text
Sales Invoice:       ACC-SINV-2026-00021
Base Amount:         ₹10,000
Rate:                5%
Commission:          ₹500
```

The ledger contains:

```text
CL-2026-00001
Entry Type:          Commission
Commission Amount:   ₹500
```

The Sales Invoice is later cancelled.

The system creates:

```text
CL-2026-00002
Entry Type:          Reversal
Commission Amount:   -₹500
Reversal Of:         CL-2026-00001
```

The ledger history is now:

```text
CL-2026-00001 → +₹500 → Original Commission
CL-2026-00002 → -₹500 → Reversal
```

Net effect:

```text
₹0
```

Nothing has been deleted or rewritten.

## Why This Design Is Auditable

The reversal model preserves three important facts:

1. The commission was originally calculated.
2. The source transaction was later cancelled.
3. The original commission was offset by a separate reversal.

This provides a much clearer audit trail than simply changing the original commission from ₹500 to ₹0.

## Best Practices

### Never Edit the Original Commission

The original Commission Ledger entry should remain unchanged.

### Use Reversal Entries

A cancellation should be represented by a separate reversal event.

### Inspect Both Entries

When investigating a cancelled transaction, look for both:

```text
Commission
```

and:

```text
Reversal
```

entries.

### Trace the Reversal

Use the **Reversal Of** field to identify the original commission ledger entry.

### Check Statement Timing

When a reversal appears to be missing from a statement, check the reversal's transaction date, statement date range, and ledger eligibility rather than modifying the original commission.

## Complete Reversal Flow

The complete process is:

```text
ERPNext Sales Invoice
        ↓
Submitted
        ↓
Commission Calculated
        ↓
Commission Ledger
        │
        │ Original Entry
        ▼
Sales Invoice Cancelled
        ↓
Reversal Processing
        ↓
Reversal Ledger Entry
        │
        ├── Entry Type: Reversal
        ├── Negative Commission Amount
        └── Reversal Of → Original Entry
```

The result is an immutable history of both the commission and its reversal.

## Related Documentation

- [Commission Ledger](../concepts/commission-ledger.md)
- [Commission Statements](../concepts/commission-statements.md)
- [Commission Lifecycle](commission-lifecycle.md)
