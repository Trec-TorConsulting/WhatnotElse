## ADDED Requirements

### Requirement: Show Profitability Script Report
The system SHALL provide a Frappe Script Report named `Whatnot Show Profitability` calculating Gross Sales, Whatnot Commission (~11%), COGS, Net Profit, and Net Margin % per broadcast.

#### Scenario: Generate show profitability report
- **WHEN** a seller runs the report for the current month
- **THEN** the report lists all completed shows with aggregated sales, fee deductions, COGS, and profit summary chart.

### Requirement: 1099-K Tax Liability Ledger
The system SHALL provide an annual tax reporting endpoint calculating total gross reportable volume, platform commissions, shipping fees, and deductible cost of goods sold.

#### Scenario: Export annual 1099-K tax summary
- **WHEN** a seller requests the 1099-K summary for tax year 2026
- **THEN** the system generates gross volume, total Whatnot fees deducted, and net business receipts.
