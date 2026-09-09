# Spec: SaaS Tenant Provisioning

## ADDED Requirements

### Requirement: Subdomain availability validation
The system SHALL validate prospective seller subdomains (e.g., `cardkings.whatnotelse.com`), ensuring alphanumeric characters, length between 3 and 30 characters, and absence of reserved names (`admin`, `app`, `api`, `mail`, `desk`, `staging`).

#### Scenario: Validating an available subdomain
- **WHEN** a prospective seller checks subdomain `cardkings`
- **THEN** the system SHALL verify that no existing `Whatnot Tenant` holds `cardkings`
- **AND** return `available: true`

#### Scenario: Rejecting a reserved or duplicate subdomain
- **WHEN** a user requests subdomain `admin` or an already claimed subdomain
- **THEN** the system SHALL reject the request
- **AND** return an informative error message

### Requirement: Automated self-service tenant provisioning
The system SHALL orchestrate tenant provisioning upon submission of the registration form, creating a `Whatnot Tenant` document, configuring tenant database isolation, and provisioning initial seller admin credentials.

#### Scenario: Self-service tenant signup
- **WHEN** a seller submits the signup wizard with email, channel name, and chosen subdomain
- **THEN** the system SHALL create a `Whatnot Tenant` record in status "Provisioning"
- **AND** create default seller profile and workspace
- **AND** advance tenant status to "Active"
- **AND** return the direct login URL `https://<subdomain>.whatnotelse.com`
