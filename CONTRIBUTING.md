# Contributing

Thank you for your interest in contributing to **ERPNext Incentive Compensation Engine**.

This project is an open-source Frappe application for commission and incentive compensation management in ERPNext. Contributions are welcome, especially improvements that make commission calculation, auditability, workflows, reporting, and ERPNext integration more reliable and easier to use.

## Before You Start

1. Read the project README.
2. Check existing issues and pull requests before starting larger changes.
3. For significant feature changes, open an issue first so the design can be discussed before implementation.
4. Keep changes focused and avoid unrelated refactoring in the same pull request.

## Development Setup

The application targets **Frappe / ERPNext v16**.

Install the application on a development site:

```bash
bench get-app https://github.com/adeysh/incentive_compensation --branch version-16
bench --site <your-site> install-app incentive_compensation
bench --site <your-site> migrate
```

Enable developer mode when developing DocTypes, reports, client scripts, and other application metadata.

## Project Structure

The main application lives under:

```text
incentive_compensation/
├── commission_engine/
│   ├── calculator.py
│   ├── commission_events.py
│   ├── engine.py
│   ├── evaluator.py
│   ├── ledger.py
│   ├── payout.py
│   ├── payout_workflow.py
│   ├── permissions.py
│   ├── resolver.py
│   ├── statement.py
│   ├── statement_resolver.py
│   ├── statement_workflow.py
│   └── transaction_builder.py
├── doctype/
├── report/
└── tests/
```

Keep business logic in the appropriate `commission_engine` modules rather than duplicating calculation or workflow logic in controllers and UI code.

## Code Style

The project uses:

- **Ruff** for Python linting and formatting
- **Prettier** for JavaScript/Vue/SCSS formatting
- **ESLint** for JavaScript linting
- **pre-commit** for automated checks

Run pre-commit against the repository:

```bash
pre-commit run --all-files
```

Before submitting a pull request, also check:

```bash
git diff --check
```

## Testing

Run the application test suite with:

```bash
bench --site <your-site> run-tests --app incentive_compensation
```

When adding or changing business logic, add or update tests that cover the behavior.

Important areas to test include:

- commission calculation
- rule matching and priority
- plan selection
- tier calculations
- Sales Team allocation
- payee resolution
- ledger creation
- idempotency
- cancellation and reversal
- statement generation
- statement workflow transitions
- payout workflow transitions
- permission checks
- report filters and totals

Prefer deterministic tests that create the data they need rather than depending on manually configured records on a developer's site.

## Database and Historical Data

Commission Ledger entries are historical audit records. Changes to commission rules or plans must not silently change previously calculated commissions.

When modifying ledger-related behavior, consider:

- immutability
- idempotency
- reversals
- source transaction references
- historical snapshots
- cancellation behavior

Similarly, generated Commission Statements represent a snapshot of eligible ledger entries and should remain auditable after generation.

## Pull Requests

A good pull request should:

- explain what changed and why
- describe any user-visible behavior changes
- include tests for new or changed behavior
- keep the scope focused
- update documentation when appropriate
- pass the project's automated checks

A useful pull request description can follow this structure:

```markdown
## What changed?

Briefly describe the change.

## Why?

Explain the problem or use case.

## How was it tested?

List the relevant tests and manual verification.

## Screenshots

Include screenshots for meaningful UI changes.
```

## Commit Messages

Use short, descriptive commit messages.

Examples:

```text
feat: add tiered commission calculation
fix: prevent duplicate commission ledger entries
refactor: simplify statement generation
test: cover payout workflow transitions
docs: improve installation instructions
```

## Adding Features

Before adding a new feature, consider whether it belongs in the current MVP scope.

The current project focuses on:

- Commission Plans
- Commission Rules
- Commission Tiers
- Commission Payees
- Commission calculation
- Commission Ledger
- Commission Statements
- Commission Payouts
- Approval workflows
- Reversals
- Reports and dashboards

Features such as quotas, complex commission splits, payroll integrations, forecasting, and AI recommendations are outside the current MVP scope.

For larger additions, open an issue first and describe:

1. the problem
2. the intended users
3. the proposed behavior
4. how it fits the existing architecture
5. how it should be tested

## Reporting Bugs

When reporting a bug, include:

- Frappe version
- ERPNext version
- application version or commit
- steps to reproduce
- expected behavior
- actual behavior
- relevant traceback or logs
- screenshots when useful

Please remove sensitive business or customer data before sharing logs or screenshots.

## Security Issues

Do not publicly disclose security vulnerabilities before they have been reviewed.

If you discover a security-sensitive issue, contact the project maintainer privately through the project's GitHub repository rather than opening a public issue containing exploit details.

## License

By contributing to this project, you agree that your contributions will be licensed under the project's **MIT License**.
