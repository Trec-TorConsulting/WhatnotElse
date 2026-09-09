## Why

Sellers on Whatnot deal with complex financial margins: high transaction volumes, Whatnot commission fees (~11%), payment processing fees, shipping costs, and varying item acquisition costs (COGS). At tax season, sellers are issued IRS 1099-K forms based on gross Stripe payouts, often causing panic if their COGS and platform fees were not tracked accurately. We need dedicated financial capabilities: automated Stripe payout statement reconciliation, show-by-show net profit analysis, item ROI reporting, and 1099-K tax liability estimates.

## What Changes

- **Stripe Payout Reconciliation Engine**:
  - New DocType `Whatnot Payout Batch`: Track payout dates, gross amount, Stripe transfer IDs, Whatnot fee deductions, and bank deposit statuses.
  - CSV parser in `whatnot_else/api/payouts.py` to ingest Stripe payout statements and match them against ingested `Whatnot Order` records.
- **Show P&L & Item ROI Reports (Frappe Script Reports)**:
  - `Whatnot Show Profitability Report`: Multi-column financial report showing Show Title, Scheduled Date, Items Staged, Items Sold, Sell-Through %, Gross Revenue, Whatnot Commission, Total COGS, Net Profit, and Net Margin %.
  - `Whatnot Item Margin Analysis`: Report breaking down item acquisition costs, target vs. realized prices, and net ROI per product category.
- **1099-K & Tax Reporting Helper**:
  - Annual payout ledger aggregator calculating gross reportable volume versus deductible expenses (platform fees, shipping, COGS).

## Whatnot Impact

Whatnot sellers get instant financial clarity. Instead of guessing whether a 3-hour card break or sneaker auction was profitable, sellers see their true net earnings immediately after fees and COGS are accounted for. Tax time becomes stress-free with 1099-K reconciliations readily available.

## Affected Modules, DocTypes & Frappe Hooks

- **Modules**: `financials`, `orders`, `live-shows`
- **DocTypes**:
  - `Whatnot Payout Batch` (new DocType)
  - `Whatnot Payout Order Link` (new child DocType)
- **Reports**:
  - `Whatnot Show Profitability`
  - `Whatnot Item Margin Analysis`
- **Frappe Hooks**: `scheduler_events` for recurring payout sync checks

## Rollback Plan

Custom reports and payout batch DocTypes can be uninstalled or dropped via Frappe bench without corrupting underlying ERPNext general ledger records.

## Capabilities

### New Capabilities
- `payout-reconciliation`: Ingest Stripe/Whatnot payout ledgers, reconcile against orders, and compute net bank deposits.
- `financial-reporting`: Script reports for per-show profitability, item-level ROI, and annual 1099-K tax breakdown.

### Modified Capabilities
<!-- None: Initial implementation of financial capabilities -->

## Impact

- **Codebase**: Adds DocType `Whatnot Payout Batch`, API module `whatnot_else/api/payouts.py`, and Frappe reports under `whatnot_else/whatnot_else/report/`.
- **Infrastructure**: No cluster manifest changes required.
