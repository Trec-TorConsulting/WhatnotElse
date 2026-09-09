## ADDED Requirements

### Requirement: AI Auction Price & Demand Optimization
The system SHALL provide an AI forecasting method in `whatnot_else/api/forecasting.py` that analyzes category trends and suggests starting auction bids and reserve recommendations.

#### Scenario: Recommend starting auction bid
- **WHEN** a seller requests pricing intelligence for a graded vintage trading card
- **THEN** Gemini generates optimal starting bid range and reserve targets to maximize auction frenzy.
