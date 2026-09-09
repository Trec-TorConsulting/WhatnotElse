## Why

WhatnotElse currently operates as a powerful backend ERP, but lacks the commercial self-service infrastructure required of a multi-tenant SaaS / PaaS. To scale commercially and attract sellers organically, WhatnotElse needs:
1. An automated self-service onboarding and subscription billing engine (PaaS layer) at `whatnotelse.com`.
2. A viral product-led growth (PLG) engine via an interactive OBS live stream broadcast overlay HUD (`/overlay`), which advertises the platform to thousands of live viewers and competing streamers on every broadcast.
3. An AI live stream audio co-pilot ("Earbud Whisperer") that delivers real-time pricing intelligence and VIP alerts directly into the streamer's ear during fast auctions.

## What Changes

- **Commercial SaaS Marketing & Self-Service Portal (`/` on root `whatnotelse.com`)**:
  - High-converting dark-mode marketing portal with glassmorphism design, interactive feature tour, pricing matrix, and 14-day free trial CTA.
  - Interactive onboarding modal collecting seller profile, Whatnot channel handle, desired subdomain (`<seller>.whatnotelse.com`), and plan tier.
- **Automated Tenant Provisioning Engine (`Whatnot Tenant` DocType)**:
  - Subdomain validation, automated tenant site initialization, administrator credentials dispatch, and tenant health status monitoring.
- **Stripe SaaS Subscription Billing (`Whatnot Subscription Plan`, `Whatnot Tenant Subscription`)**:
  - Multi-tier billing: **Starter ($49/mo)**, **Pro Streamer ($129/mo)**, and **Warehouse Enterprise ($299/mo)**.
  - Webhook listener for Stripe subscription events (`checkout.session.completed`, `invoice.payment_succeeded`, `customer.subscription.deleted`).
  - Feature gating: Restricts live multi-channel sync or warehouse tray counts based on active subscription tier.
- **Interactive OBS Live Stream Broadcast Overlay HUD (`/overlay`)**:
  - Transparent browser source page for OBS Studio / Streamlabs (`/overlay?show=SHOW-001`).
  - Real-time active lot card (slab grade badge, high-res item image, starting bid, reserve status).
  - Animated VIP Buyer alert banner (*"💎 Platinum VIP @cards_fanatic joined the stream"*).
  - Viral product-led growth footer: **`Powered by WhatnotElse ⚡ Start Free at whatnotelse.com`**.
- **AI Audio Co-Pilot ("The Earbud Whisperer")**:
  - Hands-free Bluetooth earbud audio telemetry via Web Speech API, whispering real-time auction comps and VIP bidder warnings into the streamer's ear without interrupting the broadcast.

## Whatnot Impact

Prospective sellers can sign up and launch an enterprise Whatnot operations hub in under 60 seconds with their own branded subdomain. Streamers dramatically increase stream production value with a professional OBS overlay that automatically markets WhatnotElse to every viewer and fellow seller in the chat room.

## Affected Modules, DocTypes & Frappe Hooks

- **Modules**: `saas`, `live-shows`, `billing`, `ai-features`
- **DocTypes**:
  - `Whatnot Tenant` (New DocType: tracks seller subdomain, owner email, site status, cluster host, and provisioned date)
  - `Whatnot Subscription Plan` (New DocType: tier definitions, Stripe Price IDs, monthly cost, and feature limits)
  - `Whatnot Tenant Subscription` (New DocType: maps tenant to active plan, Stripe customer ID, status, and renewal dates)
- **Web Pages**:
  - `/` (Public marketing homepage and onboarding wizard)
  - `/overlay` (Transparent OBS live stream HUD browser source)
- **Backend APIs**:
  - `whatnot_else.api.saas.check_subdomain_available`
  - `whatnot_else.api.saas.provision_tenant`
  - `whatnot_else.api.saas.create_checkout_session`
  - `whatnot_else.api.overlay.get_active_stream_telemetry`
  - `whatnot_else.api.overlay.trigger_copilot_whisper`

## Rollback Plan

Tenant records, overlay web pages, and subscription DocTypes are additive and run parallel to existing ERPNext / WhatnotElse functionality. Reverting the change leaves existing single-tenant sites completely operational.

## Capabilities

### New Capabilities
- `saas-tenant-provisioning`: Automated self-service tenant onboarding, subdomain availability validation, and provisioning orchestration.
- `saas-subscription-billing`: Stripe Checkout & customer portal subscription billing with plan feature gating.
- `live-stream-overlay-hud`: Transparent OBS Studio / Streamlabs broadcast overlay HUD with active lot cards, VIP alerts, and viral growth footer.
- `ai-audio-copilot`: Hands-free earbud voice whisperer delivering real-time pricing intelligence and bidder reputation warnings to live streamers.

### Modified Capabilities
<!-- None: All new SaaS and live stream expansion capabilities -->

## Impact

- **Codebase**: Adds SaaS DocTypes, public landing page, OBS overlay web page, and provisioning/billing APIs.
- **Infrastructure**: Leverages existing wildcard DNS (`*.whatnotelse.com`) and Traefik Gateway API; integrates Stripe API webhooks.
