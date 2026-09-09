## ADDED Requirements

### Requirement: Cross-Listing Tracking
The system SHALL provide a DocType named `Whatnot Cross Listing` mapping a `Whatnot Item` to an external listing ID and channel.

#### Scenario: Link item to external Shopify listing
- **WHEN** an item is linked to Shopify product ID "sp_987654"
- **THEN** the system tracks sync state and marks it as "Synced".
