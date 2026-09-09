## Context

Live sellers frequently experience bidding frenzies driven by high-spending enthusiasts ("whales"). Recognizing these buyers in real-time drives retention. Simultaneously, the inventory acquisition process for Whatnot sellers is uniquely unstructured (flea markets, garage sales, storage unit auctions) compared to traditional retail.

## Goals / Non-Goals

**Goals:**
- Implement `Whatnot Buyer` DocType with automated lifetime value (LTV) calculation and tier classification (`Standard`, `Silver VIP`, `Gold VIP`, `Whale VIP`).
- Automatically update buyer records when `Whatnot Order` records are created or submitted.
- Implement `Whatnot Sourcing Batch` with a child table `Whatnot Sourcing Item` to record lot purchases and auto-generate `Whatnot Item` records with distributed unit COGS.
- Expose CRM lookup endpoints in `whatnot_else/api/crm.py`.

**Non-Goals:**
- Direct Whatnot in-app live chat bot scraping (Phase 1 uses order data and manual desk lookup).

## Decisions

### 1. Dedicated Whatnot Buyer DocType vs Core ERPNext Customer
- **Choice**: Dedicated `Whatnot Buyer` DocType that maintains an optional link to ERPNext `Customer`.
- **Rationale**: Whatnot buyers are identified by their community username (e.g. `@pokemon_king99`), which does not always have real full names or billing tax info until an order is placed.

### 2. Sourcing Batch Unit COGS Distribution
- **Choice**: Support both weighted allocation (by estimated individual resale value) and equal distribution (total batch price divided by item count).
- **Rationale**: Streamlines flea market lot purchases where sellers buy a mixed box of 20 items for a flat $100.
