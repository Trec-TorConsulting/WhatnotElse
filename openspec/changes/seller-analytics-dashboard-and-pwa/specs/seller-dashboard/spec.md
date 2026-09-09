## ADDED Requirements

### Requirement: Executive Seller Analytics Dashboard
The system SHALL provide a Frappe Desk custom page named `whatnot_dashboard` displaying gross revenue, net profit, average sell-through %, and upcoming live stream broadcasts.

#### Scenario: View seller dashboard
- **WHEN** a seller accesses `/app/whatnot-dashboard`
- **THEN** the page renders KPI metric cards and charts loaded from the analytics API.
