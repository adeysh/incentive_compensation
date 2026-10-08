# Contributing

Thank you for contributing to the ERPNext Incentive Compensation Engine.

This project is a Frappe application for commission and incentive compensation processing in ERPNext. Contributions that improve correctness, usability, documentation, testing, and maintainability are welcome.

## Before You Start

Before making a change, understand the part of the application you are modifying.

The main development areas are:

```text
Commission Configuration
        ↓
Commission Calculation
        ↓
Commission Ledger
        ↓
Commission Statements
        ↓
Commission Payouts
        ↓
Reports
```

The [Architecture](architecture.md) and [Calculation Engine](calculation-engine.md) documentation are useful starting points for understanding how these components fit together.

## Development Requirements

The project is developed against:

- Frappe Framework v16
- ERPNext v16
- Python 3.14+
- A working Frappe Bench environment

You should have a development site where the application is installed.

## Getting the Application

From your Frappe Bench directory:

```bash
bench get-app https://github.com/adeysh/incentive_compensation --branch version-16
```

Install the application on a development site:

```bash
bench --site <your-site> install-app incentive_compensation
```

For example:

```bash
bench --site incentive-test.localhost install-app incentive_compensation
```

If the application is already installed, use the normal Bench workflow for updating the application and migrating the site when your changes require schema or DocType changes.

## Repository Branch

The active development branch for the application is:

```text
version-16
```

Changes intended for the Frappe v16 application should be developed against this branch unless the project specifies otherwise.

## Create a Development Branch

Create a focused branch for your change rather than working directly on the main development branch.

For example:

```bash
git checkout version-16
git pull
git checkout -b fix/commission-calculation
```

Use a branch name that makes the purpose of the change clear.

Examples:

```text
fix/tier-boundary-calculation
fix/payout-validation
feat/commission-adjustments
docs/statement-workflow
test/ledger-idempotency
```

Keep each branch focused on one logical change where possible.

## Understand the Change Before Coding

Before modifying code, identify:

1. Which user or business problem is being solved?
2. Which part of the commission lifecycle is affected?
3. Which DocTypes or engine modules are involved?
4. Whether historical commission behavior could be affected.
5. Which tests should be updated or added.

For example, a change to Commission Rule resolution may affect:

```text
resolver.py
      ↓
evaluator.py
      ↓
ledger.py
      ↓
statements
      ↓
reports
```

A change that appears small can therefore have downstream effects.

## Where to Put Code

Keep business logic in the appropriate layer.

| Area                            | Preferred Location                         |
| ------------------------------- | ------------------------------------------ |
| Mathematical calculations       | `commission_engine/calculator.py`          |
| Plan/rule/tier/payee resolution | `commission_engine/resolver.py`            |
| Calculation orchestration       | `commission_engine/evaluator.py`           |
| Transaction preparation         | `commission_engine/transaction_builder.py` |
| Ledger creation and reversal    | `commission_engine/ledger.py`              |
| Sales Invoice events            | `commission_engine/commission_events.py`   |
| Statement generation            | `commission_engine/statement.py`           |
| Statement entry resolution      | `commission_engine/statement_resolver.py`  |
| Statement workflow              | `commission_engine/statement_workflow.py`  |
| Payout creation                 | `commission_engine/payout.py`              |
| Payout workflow                 | `commission_engine/payout_workflow.py`     |
| Permission checks               | `commission_engine/permissions.py`         |
| Reports                         | `commission_engine/reports/`               |

Avoid putting commission calculation logic directly into event handlers, client scripts, or report code when it belongs in the engine.

## Keep Event Handlers Thin

ERPNext document events should primarily connect Frappe events to the commission engine.

For example:

```python
def on_sales_invoice_submit(doc, method=None):
    create_ledger_entries_for_invoice(doc)
```

The event handler should not become a second implementation of the calculation engine.

Keep the responsibilities separated:

```text
Frappe Event
     ↓
Event Handler
     ↓
Commission Engine
     ↓
Ledger
```

See [Events](events.md) for more information.

## Preserve Historical Commission Data

Historical Commission Ledger entries are an important audit boundary.

Changes must not casually rewrite historical commission calculations.

Before modifying ledger behavior, consider:

- Can an existing ledger entry be changed?
- Can the same calculation be inserted twice?
- Does the change affect reversal behavior?
- Will existing statements still represent the correct historical snapshot?
- Can reports still explain the result?

The default expectation is that historical records remain stable.

## Maintain Idempotency

Commission generation uses a source key to prevent duplicate ledger entries.

Changes to commission creation should preserve this behavior.

When modifying the ledger creation flow, test:

```text
First processing
    ↓
Ledger created

Repeated processing
    ↓
No duplicate ledger
```

A change that accidentally removes idempotency can create incorrect commission totals.

## Workflow Changes

Commission Statements and Commission Payouts use controlled workflow transitions.

Do not bypass workflow validation by introducing direct status changes unless the operation is intentionally part of the lifecycle design.

For example, statement processing follows:

```text
Generated
    ↓
Under Review
    ↓
Approved
    ↓
Posted
    ↓
Paid
```

Payout processing has its own lifecycle.

When changing a workflow:

1. Document the new transition.
2. Update workflow validation.
3. Update UI actions if necessary.
4. Add or update tests.
5. Verify invalid transitions remain blocked.

## Add Tests With Code Changes

New behavior should normally have corresponding tests.

The appropriate test layer depends on the change.

### Calculation Change

Add or update unit tests for:

- expected calculations
- boundaries
- decimal values
- edge cases

### Resolver Change

Test:

- matching
- non-matching conditions
- priorities
- validity dates
- selection behavior

### Ledger Change

Test:

- creation
- idempotency
- immutability
- reversals

### Statement Change

Test:

- eligible entry selection
- totals
- snapshot behavior
- workflow transitions
- immutability

### Payout Change

Test:

- creation
- duplicate prevention
- validation
- workflow transitions
- statement synchronization

### Event Change

Test the relevant ERPNext document lifecycle event.

### Report Change

Test:

- filters
- date ranges
- aggregation
- expected results

See [Testing](testing.md) for the broader testing strategy.

## Run Focused Tests First

During development, start with the tests related to your change.

For example, after modifying the calculation engine, run the relevant calculation tests before running the complete application suite.

Then run the broader test suite:

```bash
bench --site <your-site> run-tests --app incentive_compensation
```

Focused tests make it easier to identify the immediate source of a failure.

## Test End-to-End Changes

If a change affects multiple stages of the commission lifecycle, perform an end-to-end check.

A representative flow is:

```text
Sales Invoice
      ↓
Commission Ledger
      ↓
Commission Statement
      ↓
Under Review
      ↓
Approved
      ↓
Posted
      ↓
Commission Payout
      ↓
Paid
```

Changes affecting Sales Invoice cancellation should also verify:

```text
Sales Invoice
      ↓
Original Commission
      ↓
Cancellation
      ↓
Reversal
```

## Code Quality

The repository uses pre-commit for code formatting and linting.

Install pre-commit if it is not already available:

```bash
pip install pre-commit
```

Enable the repository hooks:

```bash
cd apps/incentive_compensation
pre-commit install
```

The repository is configured to use tools including:

- Ruff
- ESLint
- Prettier
- pyupgrade

Run the checks before submitting a change.

You can also run pre-commit manually:

```bash
pre-commit run --all-files
```

## Keep Changes Focused

Prefer small, focused changes.

For example, avoid combining:

```text
Commission calculation refactor
+
Workspace redesign
+
Documentation rewrite
+
Unrelated bug fixes
```

into one change.

Instead, separate logically independent changes so that each can be reviewed and tested clearly.

## Documentation Changes

Documentation is part of the project.

Update the relevant documentation when a change affects:

- installation
- configuration
- commission behavior
- workflows
- reports
- development architecture
- testing
- public APIs

Documentation lives under:

```text
docs/
```

The documentation site is built with MkDocs.

When adding a new documentation page:

1. Create the Markdown file under the appropriate `docs/` directory.
2. Add it to `mkdocs.yml`.
3. Check the page locally.
4. Verify links to related documentation.
5. Include screenshots or diagrams when they materially improve understanding.

## Local Documentation Preview

From the application repository:

```bash
mkdocs serve
```

The local documentation server can then be used to review changes before submitting them.

## Commit Messages

Use clear commit messages that describe the change.

Examples:

```text
feat: add commission adjustment support
fix: prevent duplicate payout creation
fix: handle tier boundary correctly
test: cover statement immutability
refactor: simplify commission rule resolver
docs: document payout workflow
```

The commit should describe the logical change rather than the individual files modified.

## Review Your Diff

Before committing, inspect the changes:

```bash
git status
git diff
```

Check for:

- accidental files
- debug statements
- generated files
- unrelated changes
- secrets or credentials
- incorrect documentation
- missing tests

Also verify that temporary files and local environment artifacts are not being committed.

## Commit the Change

After reviewing and testing:

```bash
git add <files>
git commit -m "fix: describe the change"
```

Keep the commit focused and make sure the working tree contains only the intended changes.

## Push the Branch

Push your development branch to GitHub:

```bash
git push -u origin <branch-name>
```

Then open a pull request against the appropriate project branch.

## Pull Requests

A good pull request should make it easy to understand:

- what changed
- why it changed
- how it was implemented
- how it was tested
- whether documentation was updated

A useful pull request description can include:

```text
## What changed

Brief description.

## Why

Problem or motivation.

## How

Important implementation details.

## Testing

Tests run and relevant results.

## Documentation

Documentation updated, if applicable.
```

Keep the pull request focused on the branch's intended change.

## Backward Compatibility

Before changing existing commission behavior, consider existing configurations and historical records.

Pay particular attention to:

- existing Commission Plans
- existing Commission Rules
- existing Commission Ledger entries
- generated Statements
- Posted Statements
- Payouts
- report output

A change to calculation logic can affect future transactions without necessarily being appropriate for historical records.

Historical ledger entries should remain stable unless a deliberate migration or correction strategy has been designed.

## Database and DocType Changes

Changes to DocTypes can affect existing sites.

When modifying:

- fields
- field types
- mandatory settings
- naming
- workflows
- permissions
- child tables

test the change on a development site and run the required migration.

For example:

```bash
bench --site <your-site> migrate
```

Consider how existing records will behave after the schema change.

## Security

Do not commit:

- passwords
- API keys
- access tokens
- private credentials
- local environment secrets

Review the diff before pushing:

```bash
git diff
```

If a credential is accidentally committed, removing it from the working tree alone is not sufficient. Treat the credential as exposed and rotate it.

## Reporting Bugs

When reporting a bug, provide enough information to reproduce it.

Include, when relevant:

- Frappe version
- ERPNext version
- application version or commit
- affected DocType
- configuration involved
- steps to reproduce
- expected behavior
- actual behavior
- relevant error message or traceback

For commission calculation issues, also include the relevant:

- Commission Plan
- Commission Rule
- Commission Payee
- Sales Invoice context
- expected commission
- actual commission

Do not include confidential business or customer information.

## Proposing Features

For a feature proposal, describe the problem before proposing the implementation.

A useful proposal should explain:

```text
Problem
   ↓
Current Limitation
   ↓
Proposed Behavior
   ↓
Expected Benefit
```

For commission features, also consider whether the proposed behavior affects:

- calculation
- ledger history
- statements
- payouts
- reports
- workflows
- permissions

This helps identify the complete scope of a feature before implementation begins.

## Contribution Checklist

Before opening a pull request, check:

```text
[ ] Change is focused
[ ] Code is in the appropriate module
[ ] Tests were added or updated
[ ] Relevant tests pass
[ ] Full application tests were considered
[ ] Pre-commit checks pass
[ ] Documentation was updated when needed
[ ] No secrets or local artifacts are included
[ ] Git diff was reviewed
[ ] Commit message clearly describes the change
[ ] Pull request explains the change and testing
```

## Development Philosophy

The project prioritizes:

### Correct commission calculations

Commission amounts must be predictable and testable.

### Historical integrity

Calculated commissions should remain auditable.

### Explicit workflows

Statements and payouts should follow controlled lifecycle transitions.

### Clear separation of responsibilities

Configuration, calculation, ledger storage, statements, payouts, and reporting should remain distinct.

### Small, testable components

Business logic should be divided into focused modules that can be tested independently.

### Documentation

Changes that affect users or developers should be reflected in the documentation.

## Next Step

The Development documentation is now complete:

```text
Development
├── Architecture
├── Calculation Engine
├── Events
├── Testing
└── Contributing
```

For user-facing documentation, start with [Getting Started](../getting-started/installation.md).

For understanding the internal design, start with [Architecture](architecture.md).
