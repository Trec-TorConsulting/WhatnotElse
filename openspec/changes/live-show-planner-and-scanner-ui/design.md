## Context

Whatnot live streams are fast-paced environments where sellers present, auction, and pack hundreds of products in single 2-4 hour broadcasts. Sellers need:
1. High-level visual planning of their broadcast schedule (Calendar & Kanban).
2. Frictionless inventory lookup directly from their phone camera or handheld scanner without needing to type or search through tables.
3. Physical print formats: a structured Run-of-Show cheat sheet for the streamer's desk, and 4x6 thermal label packing slips for high-volume Zebra/DYMO printers.

## Goals / Non-Goals

**Goals:**
- Provide native Frappe Desk Calendar configuration for `Whatnot Show` with color-coded status stages (`Scheduled`, `Live`, `Completed`).
- Build an interactive, dark-mode, mobile-optimized camera scanner web page at `/scanner` supporting real-time item resolution, stock updates, show staging assignment, and instant AI description generation.
- Implement HTML/CSS Print Formats:
  - `Whatnot Show Run Sheet`: printable tabular layout detailing item sequence, start price, reserve, and physical storage bin.
  - `Whatnot Thermal Packing Slip`: 4x6 inch format compliant with standard thermal label printers (Zebra ZD420/DYMO 4XL) with order barcode, buyer details, and line items.

**Non-Goals:**
- Direct hardware serial port drivers for Zebra/DYMO (standard web browser print dialogs targeting thermal 4x6 page sizes are used).
- Native iOS/Android app wrappers (addressed via responsive web design and PWA capabilities).

## Decisions

### 1. Camera Scanning Implementation
- **Choice**: Modern browser HTML5 `MediaDevices.getUserMedia` combined with the lightweight `html5-qrcode` engine loaded via CDN with manual input fallback.
- **Rationale**: Works out of the box in mobile Safari, Chrome, and desktop browsers without native app store packaging, maintaining low barrier to entry for sellers.

### 2. Live Show Calendar Hook
- **Choice**: Frappe's standard `doctype_calendar_js` hook linking `Whatnot Show` scheduled start and end timestamps.
- **Rationale**: Provides zero-overhead integration into Frappe Desk calendar views, allowing sellers to view shows alongside standard ERPNext tasks.

### 3. Print Format Architecture
- **Choice**: Jinja2 HTML/CSS print formats registered as standard Frappe Print Formats.
- **Rationale**: Frappe's built-in PDF generator (`wkhtmltopdf`) and direct browser print handle both standard letter size (Run Sheet) and 4x6 inch thermal formats seamlessly.

## Risks / Trade-offs

- **[Risk] Mobile Camera Permissions in Web Browsers** → *Mitigation*: The `/scanner` UI checks `navigator.mediaDevices` capability, displays clear permission prompts, and always maintains an immediate physical barcode scanner / manual text input field as an active fallback.
- **[Risk] 4x6 Thermal Print Margins** → *Mitigation*: CSS explicitly sets `@page { size: 4in 6in; margin: 0.1in; }` to eliminate clipping across Zebra and DYMO drivers.
