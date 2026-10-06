# Changelog

All notable changes to **ERPNext Incentive Compensation Engine** are documented here.

The `Unreleased` section contains changes that have not yet been included in a tagged release.

## [Unreleased]

## [0.1.0] - 2026-10-06

### Added

- Commission Plan management.
- Commission Rule management with Item, Item Group, Sales Person, Customer, Customer Group, and Territory matching.
- Rule priority.
- Percentage, fixed amount, and tiered calculation methods.
- Progressive Commission Tier calculations.
- Commission Payee support for Employees and Sales Partners.
- Automatic commission evaluation from submitted ERPNext Sales Invoices.
- Sales Team allocation support.
- Immutable Commission Ledger entries.
- Commission Statement generation from eligible ledger entries.
- Statement approval and posting workflow.
- Commission Payout management.
- Payout processing and payment workflow.
- Commission reversal handling when Sales Invoices are cancelled.
- Idempotent commission ledger creation.
- Historical commission snapshots to protect previously calculated commissions from later rule changes.
- Commission reports: Summary, by Payee, by Plan, by Rule, by Invoice, and by Date.
- Commission Management Workspace with KPIs and analytics.
- Role-based protection for commission management APIs and workflow actions.
- Test coverage for calculation, resolution, ledger, statements, payouts, workflows, and reporting.
- Developer documentation and contribution guidelines.

### Changed

- Improved Commission Plan and Commission Rule form organization and usability.
- Added contextual help and descriptions to commission configuration fields.
- Improved conditional visibility of Commission Rule fields based on rule and calculation type.
- Improved Commission Payee form guidance.
- Improved Commission Ledger and Commission Statement auditability through read-only historical data.
- Improved Commission Payout payment workflow so payment details are saved before a payout is marked as Paid.
- Standardized naming and user-facing terminology across commission management screens.
- Added a dedicated Commission Management Workspace as the primary operational dashboard.

### Fixed

- Prevented duplicate commission ledger entries for the same source transaction.
- Prevented modification or deletion of immutable commission ledger history.
- Prevented modification of generated commission statement snapshots.
- Enforced valid statement workflow transitions.
- Enforced valid payout workflow transitions.
- Prevented invalid payout creation from statements that are not posted.
- Ensured a paid payout updates its associated statement to Paid.
- Improved validation for required payment date and payment reference before marking payouts as Paid.

### Testing

- Completed end-to-end verification of the commission lifecycle from Sales Invoice through Commission Ledger, Statement, Approval, Posting, Payout, Processing, and Paid.
- Verified payout validation for missing payment date and payment reference.
- Verified reversal behavior and ledger idempotency.
- Verified commission reporting against generated commission data.

## Release History

No tagged public release has been published yet.

Future releases will use the following format:

```text
## [x.y.z] - YYYY-MM-DD

### Added
### Changed
### Fixed
### Removed
### Security
```
