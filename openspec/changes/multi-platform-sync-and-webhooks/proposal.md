## Why

Top Whatnot live sellers rarely sell exclusively on Whatnot; they cross-list higher-end items on eBay, Shopify, and Mercari. However, cross-listing introduces the severe risk of double-selling: an item sold live on Whatnot stream must immediately be delisted or set to zero quantity on eBay/Shopify before another buyer purchases it. We need a cross-platform synchronization bridge and a secure webhook receiver that listens for Whatnot sales events to trigger automated inventory delisting and quantity reductions across connected external channels.

## What Changes

- **External Platform Integration Channel DocType**:
  - New DocType `Whatnot Channel Bridge`: Configuration for external sales channels (`eBay`, `Shopify`, `Mercari`), API credentials, webhook verification keys, and automatic delisting rules.
- **Cross-Listing Link DocType**:
  - New DocType `Whatnot Cross Listing`: Links a `Whatnot Item` to external listing IDs (e.g. eBay Item ID, Shopify Product/Variant ID), sync statuses (`Synced`, `Delisted`, `Pending`), and last sync timestamps.
- **Secure Webhook Receiver**:
  - API endpoint `/api/method/whatnot_else.api.webhooks.handle_whatnot_webhook` in `whatnot_else/api/webhooks.py` supporting HMAC signature verification, idempotency tracking, and event handling (`order.created`, `listing.sold`, `show.completed`).
- **Automated Delisting Dispatcher**:
  - Automated trigger in `whatnot_else/api/sync.py` that receives sale events and dispatches zero-stock updates or delist requests to configured Shopify and eBay API adapters.

## Whatnot Impact

Sellers can safely cross-list their prized inventory on eBay and Shopify while hosting live Whatnot auctions. As soon as the gavel strikes and an item is marked sold on Whatnot, WhatnotElse immediately delists or adjusts the stock to 0 on external platforms, preventing cancellations, defect rates, and negative seller feedback.

## Affected Modules, DocTypes & Frappe Hooks

- **Modules**: `multi-platform`, `inventory`, `orders`
- **DocTypes**:
  - `Whatnot Channel Bridge`
  - `Whatnot Cross Listing`
- **Hooks**: `doc_events` on `Whatnot Order` to trigger immediate cross-platform inventory reductions.

## Rollback Plan

Channel bridge settings and cross-listing links can be uninstalled without affecting core catalog items or sales orders.

## Capabilities

### New Capabilities
- `channel-bridge`: Store external API credentials for eBay, Shopify, and cross-platform channels.
- `cross-listing-sync`: Link items to external channel IDs and automatically delist on sale.
- `webhook-receiver`: Secure HMAC-authenticated endpoint processing external Whatnot webhook events.

### Modified Capabilities
<!-- None: Initial implementation of multi-platform sync -->

## Impact

- **Codebase**: Adds DocTypes, `whatnot_else/api/webhooks.py`, and `whatnot_else/api/sync.py`.
