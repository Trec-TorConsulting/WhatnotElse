## ADDED Requirements

### Requirement: Responsive Mobile Scanner Web App
The system SHALL provide a web portal route at `/scanner` supporting camera-based barcode and QR scanning with real-time item resolution against the lookup API.

#### Scenario: Mobile camera scan resolution
- **WHEN** a seller points their smartphone camera at an item barcode on the `/scanner` page
- **THEN** the application detects the code, queries the backend, and displays the item name, COGS, quantity, and assigned shows.

### Requirement: Direct Show Allocation from Scanner
The scanner interface SHALL provide a quick-action button allowing the seller to add the scanned item directly to an active or upcoming live show.

#### Scenario: Quick-stage item to upcoming show
- **WHEN** a seller taps "Assign to Show" on a scanned item card
- **THEN** the system links the item to the selected `Whatnot Show` and updates its status to "Assigned to Show".
