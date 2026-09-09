## ADDED Requirements

### Requirement: Live Show Scheduling and Lifecycle
The system SHALL provide a DocType named `Whatnot Show` allowing sellers to schedule live streams, assign a title, stream date/time, category, and track status (`Draft`, `Scheduled`, `Live`, `Completed`).

#### Scenario: Schedule a new live broadcast
- **WHEN** a seller schedules a show with start time and category "Sports Memorabilia"
- **THEN** the system creates the `Whatnot Show` in `Scheduled` status and surfaces it on the streaming calendar.

### Requirement: Item Allocation to Live Shows
The system SHALL provide a child DocType named `Whatnot Show Item` linking inventory items from `Whatnot Item` to a scheduled `Whatnot Show` with custom starting auction bid and reserve price.

#### Scenario: Assign inventory to scheduled show
- **WHEN** a seller adds 10 items from catalog to an upcoming show
- **THEN** the system validates item availability, records starting auction amounts, and reserves quantities for the show run.
