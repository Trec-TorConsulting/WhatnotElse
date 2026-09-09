# Spec: Multi-Platform Sync

## Capability
Prevent overselling and maximize revenue by synchronizing inventory
status across Whatnot, eBay, Shopify, and Mercari.

## Requirements

### Requirement: Cross-listing status tracking
- Each Whatnot Item tracks listing status per platform: Whatnot, eBay, Shopify, Mercari
- Status per platform: Not Listed, Listed, Sold, Delisted

### Requirement: Inventory lock when item goes live
- When Whatnot Show starts (Phase 2: livestream.started webhook)
- All items assigned to that show are "locked" on other platforms
- Prevents concurrent sale on eBay/Shopify while item is being auctioned live

### Requirement: Conflict resolution (Whatnot wins)
- When an item is sold on Whatnot (sold=true on Show Item)
- System automatically deletes/ends listing on eBay, Shopify, Mercari
- Platform Sync Log records the action

### Requirement: Platform credential vault
- Admin stores API keys/tokens for each platform in Platform Integration DocType
- Values stored encrypted in Kubernetes Secret (env var injection)

### Requirement: Phase 1 — Manual cross-listing export
- Seller can export item list as eBay / Shopify CSV format for manual upload

### Requirement: Phase 2 — API sync
- eBay API: Create/end listings, check sold status
- Shopify API: Create/update products, inventory levels
- Sync runs on schedule (every 15 minutes) and on-demand

## Scenarios

### Scenario: Item sold on Whatnot — auto-delist from eBay
- WHEN Whatnot Order is created for item #WN-1234
- AND item has active eBay listing (ebay_listing_id populated)
- THEN system calls eBay API to end the listing
- AND Platform Sync Log entry: "eBay listing ended — item sold on Whatnot"
