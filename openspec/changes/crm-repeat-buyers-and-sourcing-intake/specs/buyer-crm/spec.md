## ADDED Requirements

### Requirement: Whatnot Buyer Profile & VIP Tier Tracking
The system SHALL provide a DocType named `Whatnot Buyer` tracking username, lifetime value (LTV), order count, VIP tier status (`Standard`, `Silver VIP`, `Gold VIP`, `Whale VIP`), and private seller notes.

#### Scenario: Automatic VIP tier upgrade
- **WHEN** a buyer's total lifetime orders exceed $1,000.00
- **THEN** the system upgrades the buyer tier to "Gold VIP" and updates their LTV metric.
