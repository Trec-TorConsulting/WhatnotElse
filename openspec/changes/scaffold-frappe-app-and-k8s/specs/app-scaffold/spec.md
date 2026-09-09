## ADDED Requirements

### Requirement: Custom Frappe App Scaffolding
The application SHALL provide a compliant Frappe Framework v16 custom application named `whatnot_else` containing `hooks.py`, `modules.txt`, `pyproject.toml`, and initialization metadata.

#### Scenario: App discovery by Frappe Bench
- **WHEN** the `whatnot_else` app directory is installed in a Frappe bench environment
- **THEN** Frappe recognizes the app, exposes its declared modules, and registers its custom hooks and assets without schema conflict.

### Requirement: Multi-Seller Profile Configuration
The system SHALL provide a DocType named `Whatnot Seller Profile` that stores seller credentials, shop subdomains, CSV profile configurations, and secure API metadata.

#### Scenario: Seller profile creation
- **WHEN** an administrator creates a `Whatnot Seller Profile` with seller slug "cardcollector"
- **THEN** the system validates uniqueness of the seller slug and associates future imports and live shows with this profile.
