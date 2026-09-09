## Context

Cross-listing is critical for inventory velocity, but double-selling can destroy a seller's account standing on eBay and Shopify. To make WhatnotElse an enterprise solution, the system must bridge the gap between live video sales and asynchronous marketplace channels.

## Goals / Non-Goals

**Goals:**
- Implement `Whatnot Channel Bridge` to store credentials for external marketplace APIs (eBay, Shopify, Mercari).
- Implement `Whatnot Cross Listing` to map items to external marketplace listing identifiers.
- Create a production-grade webhook receiver verifying HMAC SHA256 signatures against the seller's secret token.
- Automate instant delisting requests to connected channels upon Whatnot item sale.

**Non-Goals:**
- Full eBay storefront listing creator in Phase 1 (sellers create listings externally or via Whatnot; the bridge synchronizes availability, quantity, and delisting).

## Decisions

### 1. Webhook Signature Verification
- **Choice**: Standard HMAC SHA256 verification using `X-Whatnot-Signature` header against `webhook_secret` configured in `Whatnot Seller Profile`.
- **Rationale**: Rejects spoofed webhook requests and adheres to modern webhook security best practices.

### 2. Immediate Asynchronous Dispatch
- **Choice**: Execute delisting via background queue worker (`frappe.enqueue`) to ensure the webhook responder acknowledges Whatnot within <500ms while processing delisting tasks in the background.
- **Rationale**: Prevents webhook timeouts and retries while communicating with external rate-limited marketplace APIs.
