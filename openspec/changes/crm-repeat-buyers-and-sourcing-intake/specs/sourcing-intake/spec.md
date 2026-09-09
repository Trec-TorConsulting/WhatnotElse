## ADDED Requirements

### Requirement: Sourcing Batch Lot Intake
The system SHALL provide a DocType named `Whatnot Sourcing Batch` recording batch title, source vendor/location, total purchase price, and item allocation.

#### Scenario: Auto-distribute unit COGS across lot items
- **WHEN** a seller creates a sourcing batch of $200.00 with 10 items using equal distribution
- **THEN** the system sets unit COGS to $20.00 for each item and creates the corresponding `Whatnot Item` records.
