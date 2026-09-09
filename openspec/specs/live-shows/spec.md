# Spec: Live Show Planner

## Capability
Plan, manage, and analyze Whatnot live shows — from scheduling
through real-time execution to post-show performance review.

## Requirements

### Requirement: Show creation and scheduling
- Seller creates Whatnot Show with title, date/time, type, description
- Show types: Auction, BIN, Mixed, Break
- Calendar view displays all shows (planned, live, completed)

### Requirement: Item assignment and sequencing
- Seller assigns inventory items to a show via Whatnot Show Item child table
- Items can be reordered (sequence field) to define show order
- Item status changes to "Live" when show starts; "Sold" or "Relisted" when show ends

### Requirement: Show status lifecycle
Planned → Live → Completed | Cancelled

### Requirement: Post-show analytics
- After show: total revenue, total COGS, net profit, sell-through %
- Per-item performance visible in show detail view
- Unsold items are flagged for relisting

### Requirement: Break management
- For card breaks: define break slots (e.g., 30 spots at $10 each)
- Each slot can be assigned to a buyer
- System tracks break revenue separately

## Scenarios

### Scenario: Plan a show one week out
- WHEN seller creates a show for next Saturday 7pm with 40 items
- THEN show appears in calendar view
- AND all 40 assigned items show status "Listed" (not yet Live)

### Scenario: Show completes
- WHEN seller marks show status as Completed
- THEN system calculates total_sales, total_profit, platform_fees automatically
- AND all sold items are marked Sold
- AND unsold items remain Listed with a "Relist" prompt
