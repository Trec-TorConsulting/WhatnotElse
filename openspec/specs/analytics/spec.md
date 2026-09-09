# Spec: Reporting & Analytics

## Capability
Actionable dashboards and reports giving sellers deep visibility into
inventory, show performance, financial health, and buyer behavior.

## Dashboards

### Seller Dashboard (/)
- Today's orders count, today's revenue, pending to ship
- Active / upcoming show card
- Inventory health widget: total active items, total COGS
- Recent profit trend (7-day sparkline)

### Show Performance Dashboard
- Per-show: revenue, sell-through %, avg price, profit
- Top 10 shows by revenue (bar chart)
- Category breakdown per show (pie chart)

### Inventory Health Dashboard
- Items by status (donut: Listed/Live/Sold/Archived)
- Total COGS, estimated FMV, unrealized gain
- Stale inventory alert (items not in any show for >30 days)

### Platform Comparison Dashboard
- Side-by-side: Whatnot vs. eBay vs. Shopify monthly revenue
- Platform fee comparison by platform

## Reports

| Report | Description |
|--------|-------------|
| Show P&L | Gross, fees, COGS, net profit per show |
| Item Profitability | Lifetime profit per item |
| Inventory Valuation | COGS, FMV, unrealized gain |
| Top Buyers | Revenue and order count per buyer |
| Platform Revenue | Cross-platform monthly revenue |
| Annual Tax Summary | Gross payouts per year (1099-K) |
| Sourcing ROI | Profitability per sourcing run |
| Category Sell-Through | % sold per category over time period |

## Requirements

### Requirement: Real-time seller dashboard
- Dashboard loads within 3 seconds
- KPI numbers reflect current database state (no caching lag >1 min)
- Mobile-responsive: KPI cards stack vertically on small screens

### Requirement: All reports exportable
- Every report has CSV and PDF export
- Date range filters on all time-based reports
- Seller filter for Admin (to view any seller's reports)

## Scenarios

### Scenario: Seller views show P&L
- WHEN seller navigates to Show P&L report and selects last 30 days
- THEN report displays a row per completed show with all financial fields
- AND a summary totals row shows combined P&L for the period

### Scenario: Admin views all sellers' analytics
- WHEN Admin opens Platform Comparison Dashboard
- THEN all seller profiles are included in aggregate numbers
- AND a seller filter dropdown allows isolating to one seller
