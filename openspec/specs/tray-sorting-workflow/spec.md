# Spec: Tray Sorting Workflow

## Capability
Dynamic physical tray and bin management mapping live stream show orders to designated warehouse trays, with voice and sound guidance for high-speed item sorting ("Scan-to-Tray").

## Requirements

### Requirement: Physical tray allocation per buyer
The system SHALL dynamically allocate available physical fulfillment trays (e.g., Trays 1–150) to unique buyers with orders in a given live show. All items won by the same buyer within that show SHALL be assigned to that single tray.

### Requirement: Scan-to-Tray barcode identification and routing
The system SHALL resolve scanned item barcodes to their assigned tray and buyer, returning the tray number, buyer handle, and show lot number immediately.

### Requirement: Voice and audio feedback for warehouse sorting
The fulfillment interface SHALL synthesize spoken audio announcing the tray number and buyer handle (e.g., "Tray 14, Collector Dan") and play an audible chime upon successful scan.

## Scenarios

### Scenario: Allocating trays for a completed live show
- **WHEN** the warehouse operator triggers tray allocation for a live show with 45 unique buyers
- **THEN** the system SHALL assign Tray 1 through Tray 45 to the respective buyers
- **AND** the system SHALL update each Whatnot Order with its assigned tray number
- **AND** mark each assigned tray status as "Allocated"

### Scenario: Warehouse operator scans sold item barcode
- **WHEN** the operator scans an item barcode in Scan-to-Tray mode
- **THEN** the system SHALL return the assigned tray number (e.g., "Tray 14") and buyer handle (e.g., "@collector_dan")
- **AND** the UI SHALL display a high-visibility, full-screen color card with the tray number
- **AND** the system SHALL update the item allocation status to "Sorted"

### Scenario: Audio announcement on successful scan
- **WHEN** an item is successfully scanned to Tray 14
- **THEN** the client browser SHALL play a high-frequency success chime
- **AND** the client browser SHALL trigger text-to-speech audio via Web Speech API announcing "Tray 14"
- **AND** provide haptic vibration feedback on supported mobile devices

### Scenario: Unrecognized or unassigned barcode scanned
- **WHEN** an operator scans a barcode that does not belong to the active show
- **THEN** the client browser SHALL play a distinct low-pitch error buzzer
- **AND** display an error alert indicating "Item not in this show"
