# Spec: Security & Access Control

## Capability
Role-based access control, multi-seller isolation, API token authentication
for integrations, and full audit logging of all mutations.

## Roles

| Role | Permissions |
|------|------------|
| Admin | Full access — all DocTypes, settings, integrations, reports |
| Seller | Own profile's items, shows, orders; no financial admin; no other sellers' data |
| Warehouse Staff | Inventory (read/write), orders (read/write fulfillment), no financials |
| Accountant | Financial reports (read-only), payouts, tax; read-only items/orders |

## Requirements

### Requirement: Role-based DocType permissions
- Every DocType has explicit Frappe permissions for each role
- Seller role filters by linked Whatnot Seller Profile (owner isolation)
- Accountant role is read-only on all operational DocTypes

### Requirement: Multi-seller isolation
- One ERPNext installation serves multiple Whatnot seller accounts
- Each Whatnot Seller Profile is isolated — sellers cannot see each other's data
- Admin sees all sellers

### Requirement: API token auth for webhooks
- Webhook endpoint validates Authorization: Bearer {token} header
- Token is hashed and stored in Whatnot Seller Profile
- Invalid token returns 401; valid token proceeds

### Requirement: Audit log
- All DocType inserts, updates, and deletes captured
- Frappe Track Changes enabled on critical DocTypes: Whatnot Order, Whatnot Item, Whatnot Payout
- Custom Whatnot Audit Log for critical business events (price changes, payout edits)

### Requirement: Secret management
- All API keys in Kubernetes Secrets → injected as environment variables
- Frappe reads secrets from env, never from database plaintext
- secret.yaml in repo is template only (placeholder values)

## Scenarios

### Scenario: Seller cannot see another seller's items
- GIVEN two sellers: Alice and Bob
- WHEN Alice logs into Frappe Desk and views Whatnot Item list
- THEN Alice sees only her own items (filtered by seller_profile = Alice's profile)
- AND Bob's items do not appear in any list view or report

### Scenario: Webhook with invalid token is rejected
- WHEN Whatnot POST to webhook endpoint with wrong Bearer token
- THEN system returns 401 Unauthorized
- AND no order or document is created

### Scenario: Price change is audit-logged
- WHEN Admin changes floor_price on a Whatnot Item
- THEN a Whatnot Audit Log entry is created with: user, timestamp, old value, new value
