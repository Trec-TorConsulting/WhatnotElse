## ADDED Requirements

### Requirement: Whatnot Developer GraphQL Client
The system SHALL provide a dedicated client class `WhatnotGraphQLClient` in `whatnot_else/api/whatnot_client.py` configured for GraphQL queries and mutations using bearer authentication.

#### Scenario: Query Whatnot listings
- **WHEN** the client executes a query for live shows or listings
- **THEN** it passes bearer tokens and returns structured response payloads.
