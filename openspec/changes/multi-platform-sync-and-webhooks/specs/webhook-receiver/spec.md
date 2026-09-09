## ADDED Requirements

### Requirement: Secure Webhook Receiver
The system SHALL provide a webhook listener at `/api/method/whatnot_else.api.webhooks.handle_whatnot_webhook` validating HMAC signatures and triggering inventory delisting.

#### Scenario: Verified order webhook received
- **WHEN** Whatnot posts an authenticated order creation event
- **THEN** the system verifies the HMAC signature, ingests the order, and dispatches background delisting tasks.
