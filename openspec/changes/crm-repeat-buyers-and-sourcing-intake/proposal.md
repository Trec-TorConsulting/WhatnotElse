## Why

In live selling, a disproportionate percentage of high-value bids come from repeat VIP buyers. Furthermore, sourcing inventory from flea markets, garage sales, and estate liquidations is often done in bulk lots where determining individual unit COGS is difficult without intake tooling. We need a dedicated Customer/Buyer CRM for tracking repeat buyer metrics and VIP tiers, paired with a Sourcing Intake engine allowing sellers to record bulk buys, distribute purchase costs across items, and log sourcing vendors.

## What Changes

- **Customer & VIP Buyer CRM**:
  - New DocType `Whatnot Buyer`: Tracks buyer Whatnot username, VIP tier (`Standard`, `Silver VIP`, `Gold VIP`, `Whale VIP`), total lifetime spend (LTV), order frequency, favorite categories, private streamer notes, and shipping address history.
  - Automatic buyer profile updates on order confirmation.
- **Sourcing & Purchasing Intake**:
  - New DocType `Whatnot Sourcing Batch`: Records sourcing source (`Estate Sale`, `Flea Market`, `Distributor`, `Thrift`, `Private Collection`), purchase date, total lot cost, seller profile, and receipt attachment.
  - Automatic item creation and unit COGS allocation from sourcing batches into `Whatnot Item`.
- **VIP Buyer Lookup & Notes API**:
  - Endpoint `get_buyer_profile` in `whatnot_else/api/crm.py` for live streamer lookup during auctions.

## Whatnot Impact

Streamers can instantly recognize VIP buyers entering the stream chat or bidding on lots, acknowledging their loyalty and tailoring live offers. For sourcing, sellers can buy a $500 box of 50 vintage comics at an estate sale, log the batch once, and have the system automatically assign a $10 baseline COGS to each item.

## Affected Modules, DocTypes & Frappe Hooks

- **Modules**: `crm`, `purchasing`, `inventory`
- **DocTypes**:
  - `Whatnot Buyer`
  - `Whatnot Sourcing Batch`
  - `Whatnot Sourcing Item` (child table)
- **Hooks**: `doc_events` on `Whatnot Order` to update buyer LTV and order count.

## Rollback Plan

Custom CRM and sourcing DocTypes can be uninstalled without affecting core ERPNext customers or base items.

## Capabilities

### New Capabilities
- `buyer-crm`: Tracking repeat buyer usernames, lifetime order values, VIP tiers, and streamer notes.
- `sourcing-intake`: Bulk purchase batch intake, vendor tracking, and automatic unit COGS allocation across items.

### Modified Capabilities
<!-- None: Initial implementation of CRM and Sourcing capabilities -->

## Impact

- **Codebase**: Adds DocTypes under `whatnot_else/whatnot_else/doctype/` and API module `whatnot_else/api/crm.py`.
