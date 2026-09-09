# Spec: Financial / P&L

## Capability
Real-time profit/loss tracking per item, per show, and per time period,
including Stripe payout reconciliation and 1099-K tax support.

## Requirements

### Requirement: Per-item P&L calculation
- Net Profit = Sold Price - (Sold Price × platform_fee_pct) - COGS - Shipping Cost
- Available on every Whatnot Item after sale
- Lifetime P&L for items relisted and sold multiple times (tracks each event)

### Requirement: Per-show P&L report
- After show completes: total gross revenue, total platform fees, total shipping, total COGS, net profit
- Sell-through % = items sold / items in show
- Average sale price

### Requirement: Stripe payout reconciliation
- Seller imports Stripe payout CSV (or Phase 2: Stripe API)
- System matches payouts to Whatnot Orders by date range and amount
- Unmatched payouts flagged for manual review
- Reconciliation status tracked per payout

### Requirement: 1099-K tax support
- Annual Tax Summary report: total gross payouts per year per seller
- Export to CSV for tax preparer
- Flag when annual total exceeds $600 IRS threshold (configurable)

### Requirement: Platform fee ledger
- Track all platform fees paid to Whatnot
- Monthly platform fee summary
- Compare fee totals across months/years

## Scenarios

### Scenario: Show P&L after 40-item show
- GIVEN a completed show with 35 items sold at avg $22 each
- WHEN seller views Show P&L report
- THEN sees: Gross $770, Fees $84.70 (11%), Net Payout $685.30, COGS $350, Profit $335.30

### Scenario: Stripe reconciliation
- WHEN seller imports Stripe payout CSV for August
- THEN system matches $6,240 in payouts to corresponding Whatnot Orders
- AND 2 unmatched payouts ($85, $120) are flagged for review
