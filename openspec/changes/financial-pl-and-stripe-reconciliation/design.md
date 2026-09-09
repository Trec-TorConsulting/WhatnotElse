## Context

Whatnot sellers receive periodic batch payouts through Stripe Express. A single payout lump sum into their bank account often represents dozens of auction sales minus Whatnot platform commission (~11%), payment processing fees, and shipping label adjustments. Without reconciliation tooling, sellers struggle to map bank deposits to individual orders and face surprises when 1099-K tax documents are generated.

## Goals / Non-Goals

**Goals:**
- Implement `Whatnot Payout Batch` and child table `Whatnot Payout Order Link` to track Stripe deposits and associate orders.
- Provide a payout statement importer in `whatnot_else/api/payouts.py` supporting Stripe export CSVs.
- Create two Frappe Script Reports with dynamic multi-currency summaries and chart visualizations:
  - `Whatnot Show Profitability`: Show-level breakdown of revenue, platform fees, COGS, and profit.
  - `Whatnot Item Margin Analysis`: Item-level ROI and inventory turnover by category.
- Implement an annual 1099-K tax summary API calculating reportable gross receipts vs. deductible platform expenses.

**Non-Goals:**
- Direct ACH bank scraping (Plaid integration) in Phase 1 (Stripe statement CSV export is standard).
- Filing IRS forms directly with tax authorities (reports provide exportable schedule data for CPAs).

## Decisions

### 1. Frappe Script Report vs Query Report
- **Choice**: Frappe Script Reports (`.py` + `.js`).
- **Rationale**: Script reports allow complex Python math (calculating real-time COGS from inventory ledgers, computing Whatnot tiered commissions, and aggregating child order items) that standard SQL query reports struggle to express cleanly.

### 2. Payout Reconciliation Model
- **Choice**: Separate `Whatnot Payout Batch` parent DocType with linked orders.
- **Rationale**: Matches how Stripe and Whatnot group payouts, allowing sellers to audit payout date, gross sales, Whatnot deductions, and net transferred amount against their bank statement.

## Risks / Trade-offs

- **[Risk] Discrepancy between Order Gross and Stripe Payout** → *Mitigation*: The importer flags unmatched orders or fee variance exceeding 1% with an `Audit Needed` status on the batch.
