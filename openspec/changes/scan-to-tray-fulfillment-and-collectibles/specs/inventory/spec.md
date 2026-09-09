## ADDED Requirements

### Requirement: Graded collectible and authentication tracking
The system SHALL store and manage third-party authentication and grading details on Whatnot Item records, including grading company, certified numerical grade, certification number, and population report notes for trading cards, comics, and coins.

#### Scenario: Creating a graded collectible item
- **WHEN** a seller creates or imports a trading card with `is_graded` checked
- **THEN** the system SHALL allow selecting `grading_company` (PSA, BGS, CGC, SGC, PCGS, NGC)
- **AND** require or record `grade` (e.g. "PSA 10 Gem Mint", "CGC 9.8 Near Mint/Mint")
- **AND** record the unique certification number (`cert_number`)
- **AND** make the certification number searchable via barcode/QR scanner
