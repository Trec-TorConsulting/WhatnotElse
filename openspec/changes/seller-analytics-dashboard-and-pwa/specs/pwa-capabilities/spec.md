## ADDED Requirements

### Requirement: PWA Web App Manifest and Service Worker
The system SHALL expose a Web App Manifest at `/assets/whatnot_else/manifest.json` and a service worker at `/assets/whatnot_else/sw.js` enabling mobile browser installation.

#### Scenario: Mobile browser PWA install prompt
- **WHEN** a seller visits the scanner or dashboard on a mobile browser
- **THEN** the browser detects the PWA manifest and offers "Add to Home Screen".
