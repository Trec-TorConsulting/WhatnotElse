## ADDED Requirements

### Requirement: External Channel Configuration
The system SHALL provide a DocType named `Whatnot Channel Bridge` storing API tokens, platform types (`eBay`, `Shopify`, `Mercari`), and auto-delist policies.

#### Scenario: Configure eBay bridge
- **WHEN** a seller configures an eBay channel bridge with active status
- **THEN** the system validates credentials and activates cross-platform sync capabilities for that seller.
