# Installation

The ERPNext Incentive Compensation Engine is a Frappe application designed to run with ERPNext.

## Requirements

Before installing the application, make sure you have a working Frappe Bench environment with:

- Frappe Framework v16
- ERPNext v16
- Python 3.14 or newer

You should also have a site where ERPNext is already installed.

## Get the App

From your Frappe Bench directory, fetch the application from GitHub:

```bash
bench get-app https://github.com/adeysh/incentive_compensation --branch version-16
```

This downloads the application into your Bench's `apps` directory.

## Install the App

Install the application on your ERPNext site:

```bash
bench --site <your-site> install-app incentive_compensation
```

Replace `<your-site>` with the name of your Frappe site.

For example:

```bash
bench --site acme-electronics.localhost install-app incentive_compensation
```

## Run Migrations

After installing the application, run the site migration:

```bash
bench --site <your-site> migrate
```

## Verify the Installation

Check the applications installed on your site:

```bash
bench --site <your-site> list-apps
```

You should see:

```text
incentive_compensation
```

listed alongside Frappe and ERPNext.

## Open the Application

Log in to your ERPNext site and open the **Commission Management** workspace.

The workspace provides access to:

- Commission Plans
- Commission Rules
- Commission Payees
- Commission Ledger
- Commission Statements
- Commission Payouts
- Commission Reports

## Next Step

Once the application is installed, continue with the [Quick Start](quick-start.md) guide to configure your first commission setup and process a commission.
