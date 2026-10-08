# ERPNext Incentive Compensation Engine

<div class="home-hero">
  <div class="home-eyebrow">Open-source commission engine for ERPNext</div>

  <h1 class="home-title">
    Automate commissions.<br>
    <span>Reward performance.</span>
  </h1>

  <p class="home-subtitle">
    A Frappe application for calculating, tracking, reviewing, approving,
    and paying sales commissions — directly inside ERPNext.
  </p>

  <div class="home-actions">
    <a class="home-button home-button--primary" href="getting-started/installation">
      Get Started
    </a>
    <a class="home-button home-button--secondary" href="getting-started/quick-start">
      Quick Start
    </a>
    <a class="home-button home-button--secondary" href="https://github.com/adeysh/incentive_compensation">
      View on GitHub
    </a>
  </div>

  <div class="home-product-shot">
    <img src="images/commission-workspace.png" alt="Commission Management Workspace">
  </div>
</div>

<div class="home-section">
  <h2 class="home-section-title">Everything you need to manage commissions</h2>

  <p class="home-section-lead">
    Configure commission logic, calculate commissions automatically, preserve
    an auditable history, and move approved commissions through to payment.
  </p>

  <div class="feature-grid">
    <div class="feature-card">
      <div class="feature-icon">◈</div>
      <h3>Commission Plans</h3>
      <p>Define company-specific commission plans and their validity periods.</p>
    </div>

    <div class="feature-card">
      <div class="feature-icon">◇</div>
      <h3>Commission Rules</h3>
      <p>Configure percentage, fixed-amount, and tiered commission rules.</p>
    </div>

    <div class="feature-card">
      <div class="feature-icon">◎</div>
      <h3>Commission Payees</h3>
      <p>Connect commission recipients to ERPNext Sales Persons or Sales Partners.</p>
    </div>

    <div class="feature-card">
      <div class="feature-icon">▣</div>
      <h3>Commission Ledger</h3>
      <p>Keep immutable historical records of every calculated commission.</p>
    </div>

    <div class="feature-card">
      <div class="feature-icon">▤</div>
      <h3>Statements</h3>
      <p>Group eligible commissions into reviewable and auditable statement snapshots.</p>
    </div>

    <div class="feature-card">
      <div class="feature-icon">↗</div>
      <h3>Payouts & Reports</h3>
      <p>Track commission payments and analyze activity across payees, plans, rules, and invoices.</p>
    </div>

  </div>
</div>

<div class="home-section">
  <h2 class="home-section-title">From sale to payout</h2>

  <p class="home-section-lead">
    The engine connects directly to the ERPNext sales lifecycle while keeping
    calculation, historical records, approval, and payment processing separate.
  </p>

  <div class="lifecycle">

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

  </div>
</div>

<div class="home-section">
  <h2 class="home-section-title">Built for auditability</h2>

  <p class="home-section-lead">
    Commission Ledger entries preserve the result of the calculation at the
    time the transaction was processed. Later changes to commission plans or
    rules do not rewrite historical calculations.
  </p>

  <div class="docs-cta">
    <h2>Ready to run your first commission?</h2>
    <p>
      Install the application and follow the Quick Start guide to configure a
      plan, rule, and payee, then process a complete commission lifecycle.
    </p>

    <div class="home-actions">
      <a class="home-button home-button--primary" href="getting-started/quick-start/">
        Start the Quick Start
      </a>
      <a class="home-button home-button--secondary" href="concepts/overview/">
        Explore the Concepts
      </a>
    </div>

  </div>
</div>
