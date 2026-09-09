# Spec: SaaS Subscription Billing

## ADDED Requirements

### Requirement: Multi-tier subscription plan management
The system SHALL support tiered subscription plans (`Whatnot Subscription Plan`):
- **Starter ($49/mo)**: Up to 5 shows/month, single user, basic scanning.
- **Pro Streamer ($129/mo)**: Unlimited shows, 50 fulfillment trays, multi-platform sync, AI listing copywriter.
- **Warehouse Enterprise ($299/mo)**: Unlimited shows, unlimited trays, custom OBS overlay, dedicated AI audio co-pilot.

#### Scenario: Retrieving active plans
- **WHEN** the marketing pricing page requests available subscription tiers
- **THEN** the system SHALL return the active plans, prices, and feature list

### Requirement: Stripe Checkout session creation
The system SHALL generate a secure Stripe Checkout Session URL for new tenant subscriptions or plan upgrades.

#### Scenario: Creating a checkout session
- **WHEN** an authenticated tenant selects the Pro Streamer plan
- **THEN** the system SHALL create a Stripe Checkout session with the tenant ID in metadata
- **AND** return the Stripe Checkout redirect URL

### Requirement: Subscription feature gating
The system SHALL evaluate tenant feature entitlements against their active subscription plan, blocking restricted features with an upgrade prompt.

#### Scenario: Enforcing plan limits
- **WHEN** a tenant on the Starter plan attempts to activate multi-channel eBay sync
- **THEN** the system SHALL reject the action
- **AND** return `upgrade_required: true` with a link to the billing upgrade portal
