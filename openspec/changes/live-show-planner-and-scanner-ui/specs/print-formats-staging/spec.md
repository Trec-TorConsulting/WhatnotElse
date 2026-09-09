## ADDED Requirements

### Requirement: Run-of-Show Staging Print Format
The system SHALL provide a print format named `Whatnot Show Run Sheet` for `Whatnot Show` displaying lot sequencing, starting bids, reserve prices, COGS, and lot statuses in a printable document.

#### Scenario: Print broadcast run sheet
- **WHEN** a seller prints the Run Sheet for a scheduled show
- **THEN** the system generates a formatted table of all staged items ordered for broadcast reference.

### Requirement: 4x6 Thermal Packing Slip Format
The system SHALL provide a 4x6 inch thermal print format named `Whatnot Thermal Packing Slip` for `Whatnot Order` formatted for Zebra and DYMO thermal label printers.

#### Scenario: Print thermal packing slip
- **WHEN** a warehouse packer prints a packing slip for a Whatnot order
- **THEN** the output fits exactly on 4x6 inch thermal media with USPS tracking barcode, buyer username, and packed items.
