# Spec: Order Management

## Capability
Full order lifecycle from Whatnot sale event to fulfillment closure,
supporting both CSV import (Phase 1) and real-time API/webhook (Phase 2).

## Requirements

### Requirement: CSV order import (Phase 1)
- Seller uploads Whatnot orders CSV export
- System creates Whatnot Order for each row
- Auto-creates ERPNext Customer if buyer is new (keyed by whatnot_username)
- Auto-creates ERPNext Sales Order from Whatnot Order
- Duplicate protection: skip if whatnot_order_id already exists

### Requirement: Webhook order receiver (Phase 2)
- POST /api/method/whatnot_else.api.webhooks.handle
- HMAC signature verification before processing
- Idempotent: re-delivery of same event does not create duplicate

### Requirement: Order lifecycle management
- Status transitions: Pending → Processing → Packed → Label Printed → Shipped → Delivered
- Status transitions: any → Cancelled | Refunded
- Seller can manually advance status
- Automated status update via webhook (Phase 2)

### Requirement: ERPNext integration
- Each Whatnot Order creates / links to ERPNext Sales Order
- When order is fulfilled, creates Delivery Note
- Payment (net payout) links to Payment Entry

### Requirement: Order detail view
- Shows: buyer, items, prices, platform fee, net payout, status timeline
- Shows: tracking number, label URL, packing slip link
- Action buttons: Print Label, Print Packing Slip, Mark Shipped, Mark Delivered

## Scenarios

### Scenario: Import orders from show day CSV
- WHEN seller imports CSV with 35 orders from today's show
- THEN 35 Whatnot Orders are created
- AND 35 corresponding ERPNext Sales Orders are created
- AND 12 new Customers are created (existing 23 linked to existing customer records)

### Scenario: Duplicate import protection
- WHEN seller imports the same CSV a second time
- THEN system skips all 35 rows (already exist by whatnot_order_id)
- AND seller sees summary: "0 created, 0 updated, 35 skipped (duplicate)"

### Scenario: Webhook order.created event
- WHEN Whatnot POSTs order.created webhook
- THEN HMAC signature is verified
- AND Whatnot Order is created if not already existing
- AND ERPNext Sales Order is created
