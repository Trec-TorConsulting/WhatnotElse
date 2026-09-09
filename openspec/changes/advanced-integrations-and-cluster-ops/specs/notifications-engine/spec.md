## ADDED Requirements

### Requirement: Order & Restock SMS Notifications
The system SHALL provide notification dispatchers in `whatnot_else/api/notifications.py` capable of sending transactional SMS alerts via Twilio and system emails.

#### Scenario: Send high-value order SMS alert
- **WHEN** an order exceeding $500 is placed by a VIP buyer
- **THEN** the system dispatches an SMS notification to the seller's registered phone number.
