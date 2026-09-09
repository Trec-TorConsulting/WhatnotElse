## ADDED Requirements

### Requirement: Combined shipment weight and carrier tier advisor
The system SHALL aggregate the weights of all items assigned to a single buyer or fulfillment tray and notify the seller if the bundled weight exceeds standard shipping tier thresholds (e.g., USPS Ground Advantage 16 oz threshold or Priority cubic tier changes).

#### Scenario: Multi-lot order exceeds First-Class / Ground Advantage 1lb limit
- **WHEN** a buyer wins 8 items whose combined weight is 22 oz
- **THEN** the system SHALL flag the fulfillment tray with "Weight Warning: 22 oz (Over 1 lb)"
- **AND** advise the seller to update the package weight tier on Whatnot before generating the final shipping label

### Requirement: Audio-guided fulfillment cues and speech synthesis
The fulfillment station web application SHALL utilize native browser Web Audio and Web Speech APIs to deliver instantaneous auditory feedback for warehouse operators without requiring external audio asset downloads.

#### Scenario: Spoken tray announcement
- **WHEN** an item is scanned in sorting mode
- **THEN** the browser audio subsystem SHALL announce the target tray number using local text-to-speech synthesis
- **AND** play synthesized tones (Sine wave frequency sweeps) for success and error states
