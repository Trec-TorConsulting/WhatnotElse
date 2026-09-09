## Why

Sellers on Whatnot need real-time, high-speed operational tools directly before and during live stream broadcasts. Navigating standard ERP table grids while live streaming or staging physical inventory in a warehouse is slow and error-prone. We need dedicated front-end visual workflows: an interactive Streaming Schedule Calendar & Kanban planner for live broadcasts, a mobile camera-based barcode/QR scanner web page for rapid physical inventory lookups, and printable PDF run-of-show staging sheets and thermal packing slips (DYMO/Zebra).

## What Changes

- **Interactive Streaming Schedule Calendar & Kanban**:
  - Custom Frappe Desk calendar view definition for `Whatnot Show` (`whatnot_show_calendar.js`).
  - Kanban board view definition for `Whatnot Show` tracking streams through Draft → Scheduled → Live → Completed.
- **Mobile Camera Barcode & QR Scanner Web App**:
  - Full-screen, responsive, camera-enabled web application (`/apps/whatnot_else/www/scanner.html` & `scanner.js`) utilizing HTML5 camera APIs / ZXing / Html5-QRCode with dark mode aesthetics.
  - Real-time resolution against the `/api/method/whatnot_else.api.lookup.lookup_item_by_code` endpoint.
  - Direct actions on scanned items: View COGS, adjust quantity, assign to active/upcoming live show, or trigger Gemini listing rewrite.
- **Run-of-Show Staging & Thermal Packing Slip Print Formats**:
  - `Whatnot Show Run Sheet` print format: printable staging sheet for the streamer listing lot order, starting bids, reserve prices, and item locations.
  - `Whatnot Thermal Packing Slip` print format: 4x6 thermal printer-optimized format for Zebra / DYMO printers with USPS barcode placeholder, buyer username, and item details.

## Whatnot Impact

During live streaming, sellers cannot fumble with laptops. With the mobile camera scanner, sellers can grab an item in the room, scan its barcode with their smartphone, instantly verify purchase price (COGS) and recommended starting bid, or allocate it to the active broadcast with one tap. The printed run-of-show sheet gives streamers a physical cheat-sheet at their broadcast desk.

## Affected Modules, DocTypes & Frappe Hooks

- **Modules**: `live-shows`, `inventory`, `fulfillment`
- **DocTypes**:
  - `Whatnot Show` (added calendar view and run-of-show print format)
  - `Whatnot Item` (scanner linkage)
  - `Whatnot Order` (added 4x6 thermal packing slip print format)
- **Web Pages**: `/scanner` (Frappe custom web portal route)
- **Frappe Hooks**: `doctype_calendar_js`, `website_route_rules`

## Rollback Plan

Frontend print formats, calendar JS configurations, and web routes can be reverted without database schema mutations. Disabling the scanner route simply removes access to the `/scanner` web endpoint.

## Capabilities

### New Capabilities
- `show-calendar-kanban`: Calendar and visual status workflow for scheduling and managing live shows.
- `mobile-scanner-ui`: Mobile camera-driven barcode and QR scanner web application with rapid item lookup and show assignment.
- `print-formats-staging`: Run-of-show broadcast staging sheets and Zebra/DYMO 4x6 thermal packing slips.

### Modified Capabilities
<!-- None: Initial implementation of visual UI capabilities -->

## Impact

- **Codebase**: Adds client-side assets (`public/js/`), custom web page (`www/scanner.*`), and print format templates.
- **Infrastructure**: No cluster manifest changes required; assets served via Frappe web gunicorn/nginx layer.
- **Dependencies**: Uses client-side HTML5 camera APIs (no external backend dependencies required).
