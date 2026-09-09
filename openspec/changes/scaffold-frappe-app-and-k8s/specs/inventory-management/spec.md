## ADDED Requirements

### Requirement: Master Item Inventory Catalog
The system SHALL provide a DocType named `Whatnot Item` recording item name, SKU, condition, category, COGS (Cost of Goods Sold), buy price, target reserve/listing price, and barcode/QR metadata.

#### Scenario: Item creation with COGS
- **WHEN** a seller creates a `Whatnot Item` with purchase price $40.00 and category "Trading Cards"
- **THEN** the system saves the item record, computes baseline inventory valuation, and generates or verifies the barcode string.

### Requirement: Barcode and QR Lookup Integration
The system SHALL provide mobile-accessible query endpoints to resolve a `Whatnot Item` by its scanned barcode or QR code.

#### Scenario: Mobile barcode scan lookup
- **WHEN** a user scans or submits an item barcode via the lookup endpoint
- **THEN** the system returns the matched `Whatnot Item` record details, current quantity, and allocated live shows.
