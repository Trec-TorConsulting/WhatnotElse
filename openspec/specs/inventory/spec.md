# Spec: Inventory Management

## Capability
Complete lifecycle management of all items a Whatnot seller owns, from acquisition
through listing, live show appearance, sale, and archival.

## Requirements

### Requirement: Item creation with Whatnot attributes
- Seller can create a Whatnot Item linked to an ERPNext Item
- Item captures: category, subcategory, condition, grade, grading company, set/year
- Item has internal fields: SKU, COGS, purchase source (hidden from buyers)
- Item has pricing fields: whatnot_price, floor_price, bin_price

### Requirement: Bulk CSV import
- Seller can upload Whatnot inventory export CSV
- System maps CSV columns to Whatnot Item fields
- Duplicate detection by whatnot_listing_id or SKU
- Import summary report (created, updated, skipped, errors)

### Requirement: Barcode/QR mobile lookup
- Each item has a barcode (UPC/EAN/internal) and QR code
- Mobile user navigates to /scan, scans barcode/QR
- System loads item card instantly (name, photo, condition, price, status)

### Requirement: Category-specific attributes
- Trading cards: set, year, player/character, parallel/variant, PSA/BGS grade
- Coins: denomination, mint year, mint mark, PCGS/NGC grade
- Sneakers: brand, style, size (US/EU), colorway, condition
- Clothing: brand, size, era, style
- General items: flexible custom field set

### Requirement: Graded collectible and authentication tracking
The system SHALL store and manage third-party authentication and grading details on Whatnot Item records, including grading company, certified numerical grade, certification number, and population report notes for trading cards, comics, and coins.

### Requirement: Inventory valuation
- Dashboard widget: total items by status (Listed, Live, Sold, Archived)
- Total COGS of active inventory
- Unrealized gain (estimated FMV - COGS) for listed items

### Requirement: Status lifecycle
Draft → Listed → Live (in show) → Sold | Relisted | Archived

### Requirement: Reorder alerts
- Seller configures reorder point per category or item group
- System sends email notification when active inventory falls below threshold

## Scenarios

### Scenario: Bulk import 50 items from CSV
- WHEN seller uploads Whatnot inventory CSV with 50 rows
- THEN 50 Whatnot Item docs are created (or updated if exist)
- AND seller sees import summary: "50 created, 0 updated, 0 skipped"

### Scenario: Mobile barcode scan
- WHEN seller scans item barcode on phone at /scan
- THEN item card loads within 2 seconds showing name, photo, grade, price

### Scenario: Item sold in show
- WHEN a Whatnot Show Item row is marked sold=true
- THEN linked Whatnot Item status changes to "Sold"
- AND item is removed from available inventory count

### Scenario: Creating a graded collectible item
- WHEN a seller creates or imports a trading card with `is_graded` checked
- THEN the system SHALL allow selecting `grading_company` (PSA, BGS, CGC, SGC, PCGS, NGC)
- AND require or record `grade` (e.g. "PSA 10 Gem Mint", "CGC 9.8 Near Mint/Mint")
- AND record the unique certification number (`cert_number`)
- AND make the certification number searchable via barcode/QR scanner
