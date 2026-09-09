# Spec: Scan-to-Box Verifier

## ADDED Requirements

### Requirement: Tray box audit initiation
The system SHALL allow warehouse staff to select or scan a physical tray barcode to begin packing verification for that buyer's order.

#### Scenario: Opening tray for packing
- **WHEN** staff scans barcode "TRAY-14" in Scan-to-Box mode
- **THEN** the system SHALL load the buyer details, expected item list, cumulative weight, and show order IDs for Tray 14
- **AND** the UI SHALL display the packing progress as 0% verified

### Requirement: Item-by-item scan verification
When packing items from the tray into the box, the operator SHALL scan each item. The system SHALL verify that the scanned item belongs to the active tray.

#### Scenario: Correct item scanned into box
- **WHEN** the operator scans an item that belongs to Tray 14
- **THEN** the system SHALL mark that item as "Packed"
- **AND** play an affirmative confirmation chime
- **AND** increment the progress counter (e.g., 3 of 5 items packed)

#### Scenario: Incorrect item scanned into box (mis-ship prevention)
- **WHEN** the operator scans an item that does NOT belong to Tray 14
- **THEN** the system SHALL immediately play an urgent error alarm
- **AND** trigger haptic vibration
- **AND** display a prominent red warning modal identifying the item and its actual assigned tray

### Requirement: Complete order validation and label printing trigger
When all items for a tray have been verified, the system SHALL indicate 100% completion and allow one-touch thermal label printing.

#### Scenario: All tray items packed
- **WHEN** the last item in Tray 14 is scanned
- **THEN** the UI SHALL flash a green completion banner
- **AND** play a celebratory completion chime
- **AND** update the Whatnot Fulfillment Tray status to "Ready to Pack" / "Packed"
- **AND** present a "Print 4x6 Label & Packing Slip" action button
