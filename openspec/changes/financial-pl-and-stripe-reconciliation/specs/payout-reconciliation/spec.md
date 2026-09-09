## ADDED Requirements

### Requirement: Whatnot Payout Batch Recording
The system SHALL provide a DocType named `Whatnot Payout Batch` recording payout date, Stripe transfer reference, gross sales, platform fees, shipping fees, net deposit amount, and reconciliation status.

#### Scenario: Create payout batch
- **WHEN** a seller records or imports a Stripe payout batch of $1,500.00
- **THEN** the system logs the batch, links matched `Whatnot Order` records, and marks the batch as "Reconciled" or "Discrepancy".
