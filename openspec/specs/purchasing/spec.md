# Spec: Purchasing / Restocking

## Capability
Track inventory acquisition from all sources — distributors, flea markets, estate sales —
and maintain vendor relationships and reorder intelligence.

## Requirements

### Requirement: Purchase order workflow
- Create PO linked to a vendor (distributor, flea market, estate sale, auction house)
- Receive inventory against PO → creates Whatnot Items with COGS from PO cost
- ERPNext Purchase Order and Material Receipt integration

### Requirement: Sourcing run (flea market / estate sale mode)
- Personal Shopper mode: Seller creates a "Sourcing Run" (location, date, budget)
- Add items found during the run (quick mobile entry via /scan or /source-run)
- Run summary: total spent, items acquired, projected profit

### Requirement: Reorder alerts
- Seller sets reorder point per category (e.g., Trading Cards: alert when < 20 items Listed)
- System sends email notification when active inventory drops below threshold

## Scenarios

### Scenario: Estate sale sourcing run
- WHEN seller creates Sourcing Run "Sunday Estate Sale, Sept 14"
- AND adds 8 items (total spent $145)
- THEN system creates 8 Whatnot Items with COGS pre-filled from sourcing run unit costs
- AND Sourcing Run shows projected profit based on whatnot_price vs COGS

### Scenario: Low inventory alert
- WHEN Trading Cards active inventory drops to 18 items (threshold: 20)
- THEN seller receives email: "Low Inventory Alert: Trading Cards — 18 items remaining"
