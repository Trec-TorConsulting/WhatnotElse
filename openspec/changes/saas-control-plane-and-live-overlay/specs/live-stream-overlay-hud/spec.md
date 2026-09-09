# Spec: Live Stream Overlay HUD

## ADDED Requirements

### Requirement: Real-time broadcast overlay telemetry
The system SHALL expose an endpoint `/api/method/whatnot_else.api.overlay.get_active_stream_telemetry` returning real-time stream status, active lot number, title, starting bid, current bid, PSA/BGS grading badges, and summary stream stats (orders, total sales).

#### Scenario: OBS Browser Source querying stream telemetry
- **WHEN** an OBS Browser Source requests the overlay telemetry for show `SHOW-001`
- **THEN** the system SHALL return the active auction lot data, bidding figures, and VIP buyer alerts
- **AND** include product-led growth (PLG) branding metadata

### Requirement: Transparent OBS overlay HUD interface
The system SHALL serve a dedicated web route `/overlay` optimized for OBS Studio and Streamlabs browser sources with a transparent canvas (`background: transparent !important`).

#### Scenario: Displaying active lot card
- **WHEN** a viewer or streamer views the OBS overlay canvas
- **THEN** the system SHALL render a glassmorphic lower-third card displaying the current lot, live bids, and grading certificates
- **AND** highlight real-time bid increases with dynamic CSS animations

### Requirement: Product-led growth (PLG) viral branding footer
The system SHALL display an unobtrusive, high-conversion branding footer in the overlay canvas:
`Powered by WhatnotElse ⚡ Start Free at whatnotelse.com`

#### Scenario: Viewer observing the broadcast overlay
- **WHEN** the live stream broadcasts with the overlay enabled
- **THEN** viewers and prospective streamers SHALL see the clickable / observable WhatnotElse badge and call-to-action
