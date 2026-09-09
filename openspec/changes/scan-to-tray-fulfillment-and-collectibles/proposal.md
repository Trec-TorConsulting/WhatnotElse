## Why

Fast-paced Whatnot live streams often result in buyers winning multiple auction lots across a single broadcast. Sorting hundreds of loose sold items into individual customer shipments is currently the biggest operational bottleneck and source of costly mis-ship errors for high-volume sellers. Sellers are forced to adopt external, disconnected single-purpose tools like Scan2Tray or risk shipping wrong items. 

Furthermore, high-volume Whatnot niches (Trading Cards, Comics, Coins) rely heavily on third-party authentication and grading (PSA, BGS, CGC, PCGS). Adding a physical tray-sorting system ("Scan-to-Tray"), audio-guided packing verification ("Scan-to-Box"), combined weight optimization, and certified collectible tracking bridges these critical gaps, elevating WhatnotElse beyond standalone tools.

## What Changes

- **Whatnot Fulfillment Tray Engine (`Whatnot Fulfillment Tray` DocType)**:
  - Physical bin/tray management system mapping show orders to designated tray numbers (1–150).
  - Dynamic tray allocation: Automatically groups all auction lots won by a unique buyer in a show into an assigned tray.
  - Tray status lifecycle: `Available` → `Allocated` → `Sorting` → `Ready to Pack` → `Packed` → `Shipped`.
- **Scan-to-Tray Warehouse Web App (`/pack` or enhanced `/scanner`)**:
  - High-throughput mobile/desktop sorting interface.
  - **Scan-to-Tray Mode (Sorting)**: Warehouse staff scans item barcode → Screen flashes high-visibility Tray number with buyer handle and plays an audible synthesized voice/chime (e.g., "Tray 14 - @collector_dan") → item is dropped into bin.
  - **Scan-to-Box Mode (Verification)**: Staff selects/scans Tray 14 → scans items into shipping box. Real-time item verification prevents packing incorrect items via an audible error buzzer and haptic feedback.
  - Visual completion tracker: Green verified state when 100% of order items are placed into the box.
- **Combined Shipping Weight & Tier Advisor**:
  - Automatically calculates cumulative order item weight (`weight_oz`).
  - Alerts sellers when bundled lots exceed USPS First-Class/Ground Advantage weight brackets and require label weight upgrades before printing.
- **Collectibles & Graded Card Vault Metadata**:
  - Extend `Whatnot Item` with first-class fields: `grading_company` (PSA, BGS, CGC, SGC, PCGS, NGC), `grade` (e.g., Gem Mint 10, CGC 9.8), `cert_number`, and `pop_report_notes`.

## Whatnot Impact

High-volume Whatnot sellers can eliminate post-show fulfillment chaos. Instead of scrambling through piles of sold items, warehouse staff can sort an entire 200-item live show in under 20 minutes using voice-guided tray allocation, and pack orders with zero mis-ships thanks to scan-to-box verification. Collectibles streamers gain instant indexing and verification of high-value graded cards and slabs.

## Affected Modules, DocTypes & Frappe Hooks

- **Modules**: `fulfillment`, `inventory`, `orders`
- **DocTypes**:
  - `Whatnot Fulfillment Tray` (New DocType: tracks Tray #, Show, Buyer, Item allocations, and packed state)
  - `Whatnot Item` (Modified: added grading fields `grading_company`, `grade`, `cert_number`, `is_graded`)
  - `Whatnot Order` (Modified: linked to `fulfillment_tray`, combined weight tracking)
- **Web Pages / APIs**:
  - `/pack` web page with dual-mode Scan-to-Tray and Scan-to-Box UI.
  - Backend API methods: `whatnot_else.api.fulfillment.allocate_show_trays`, `whatnot_else.api.fulfillment.scan_item_to_tray`, `whatnot_else.api.fulfillment.verify_box_item`.
- **Frappe Hooks**: `doc_events` on `Whatnot Order` for tray allocation and shipping status synchronization.

## Rollback Plan

The new `Whatnot Fulfillment Tray` DocType and custom web routes can be uninstalled without affecting existing `Whatnot Order` or `Whatnot Item` records. Added fields on `Whatnot Item` are optional and non-breaking.

## Capabilities

### New Capabilities
- `tray-sorting-workflow`: Dynamic physical tray/bin allocation and scan-to-tray voice/audio routing for multi-item live shows.
- `scan-to-box-verifier`: Item-by-item packing verification preventing mis-ships with audible success chimes and error alarms.

### Modified Capabilities
- `fulfillment`: Extended to support multi-item tray sorting, audible packing cues, and combined parcel weight advising.
- `inventory`: Extended to support authenticated collectible and graded card metadata (PSA, BGS, CGC, cert numbers).

## Impact

- **Codebase**: Adds DocType `Whatnot Fulfillment Tray`, warehouse web page `/pack` with Web Audio API sound synthesis, and backend fulfillment APIs.
- **Infrastructure**: No new Kubernetes services required; uses existing Frappe web tier and longhorn persistent storage.
- **Dependencies**: Uses native Web Audio API and Web Speech API (`SpeechSynthesisUtterance`) in the browser—zero external npm or audio file dependencies required.
