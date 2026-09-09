# Spec: Fulfillment & Shipping

## Capability
Streamlined packing and shipping workflow for high-volume Whatnot show days,
supporting bulk label printing (Zebra/DYMO), scan-to-pack on mobile, multi-item tray sorting,
and voice/audio-guided packing verification.

## Requirements

### Requirement: Packing station mobile page
- /packing-station page is mobile-optimized
- Seller scans order barcode → order card appears with items to pack
- Seller confirms packed → order status moves to Packed

### Requirement: Shipping label printing
- Phase 1: display Whatnot-generated label URL for manual download
- Phase 2: direct USPS/EasyPost API label generation
- Bulk print: select N orders → print all labels as one print job
- Zebra ZPL format for ZPL printers; PDF for other printers

### Requirement: Packing slip PDF
- Frappe Print Format: Whatnot Packing Slip
- Includes: order ID, buyer name, items, thank-you message, seller branding
- Auto-generated when order moves to Processing status

### Requirement: Tracking number management
- Seller enters tracking number after shipping
- System updates Whatnot Order status to Shipped
- Phase 2: tracking auto-populated from label API

### Requirement: Batch shipment management
- Seller can create a Shipment Batch (group of orders shipped together)
- Batch shows total items, total weight, total labels printed

### Requirement: Combined shipment weight and carrier tier advisor
The system SHALL aggregate the weights of all items assigned to a single buyer or fulfillment tray and notify the seller if the bundled weight exceeds standard shipping tier thresholds (e.g., USPS Ground Advantage 16 oz threshold or Priority cubic tier changes).

### Requirement: Audio-guided fulfillment cues and speech synthesis
The fulfillment station web application SHALL utilize native browser Web Audio and Web Speech APIs to deliver instantaneous auditory feedback for warehouse operators without requiring external audio asset downloads.

## Scenarios

### Scenario: Bulk label print after show
- WHEN seller selects 35 packed orders and clicks Print Labels
- THEN a print dialog opens with all 35 labels as a single PDF
- AND each order status is updated to Label Printed

### Scenario: Scan-to-pack a single order
- WHEN warehouse staff scans order barcode on /packing-station
- THEN order detail card appears with item list
- WHEN staff taps Confirm Packed
- THEN order status moves to Packed

### Scenario: Multi-lot order exceeds First-Class / Ground Advantage 1lb limit
- WHEN a buyer wins 8 items whose combined weight is 22 oz
- THEN the system SHALL flag the fulfillment tray with "Weight Warning: 22 oz (Over 1 lb)"
- AND advise the seller to update the package weight tier on Whatnot before generating the final shipping label

### Scenario: Spoken tray announcement
- WHEN an item is scanned in sorting mode
- THEN the browser audio subsystem SHALL announce the target tray number using local text-to-speech synthesis
- AND play synthesized tones (Sine wave frequency sweeps) for success and error states
