## ADDED Requirements

### Requirement: Whatnot Seller Hub CSV Ingestion
The system SHALL provide a CSV import parser for Whatnot order exports to extract order IDs, buyer usernames, sale prices, platform fees (~11%), shipping fees, and tracking numbers.

#### Scenario: Successful batch CSV import
- **WHEN** a seller uploads a valid Whatnot Seller Hub orders CSV export
- **THEN** the parser creates or updates `Whatnot Order` records and computes total net payout and platform fee deductions without duplicate entries.

### Requirement: ERPNext Sales Order Synchronization
The system SHALL map each validated `Whatnot Order` to an ERPNext `Sales Order` record, updating stock ledger quantities and financial ledger accounts.

#### Scenario: Generate ERPNext Sales Order from Whatnot Order
- **WHEN** a `Whatnot Order` is confirmed from CSV import
- **THEN** the system generates an ERPNext `Sales Order` linked to the buyer and seller profile with proper tax and fee allocations.
