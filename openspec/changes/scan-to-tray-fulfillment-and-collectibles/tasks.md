## 1. DocType Definitions & Schemas

- [x] 1.1 Create `Whatnot Fulfillment Tray` DocType (`whatnot_fulfillment_tray.json`, `.py`) with fields for tray number, show reference, buyer reference, status lifecycle, item counts, total weight in oz, and weight warning flag.
- [x] 1.2 Create `Whatnot Fulfillment Tray Item` child table (`whatnot_fulfillment_tray_item.json`, `.py`) linking item barcodes, lot numbers, titles, and verification status.
- [x] 1.3 Add certified collectible fields to `Whatnot Item` (`is_graded`, `grading_company`, `grade`, `cert_number`, `pop_report_notes`).
- [x] 1.4 Add `fulfillment_tray` link field to `Whatnot Order` to connect orders directly to physical sorting bins.

## 2. Backend Fulfillment APIs

- [x] 2.1 Implement `whatnot_else.api.fulfillment.allocate_show_trays(show_name)` to automatically partition all unique buyers in a show into numbered physical trays.
- [x] 2.2 Implement `whatnot_else.api.fulfillment.scan_item_to_tray(barcode, show_name)` to resolve scanned items to their assigned tray, mark items sorted, and return routing metadata.
- [x] 2.3 Implement `whatnot_else.api.fulfillment.verify_box_item(tray_name, barcode)` to audit items placed into shipping boxes, preventing mis-ships with instant validation.
- [x] 2.4 Implement `whatnot_else.api.fulfillment.calculate_combined_weight(tray_name)` to tally cumulative item weights and calculate USPS shipping bracket warnings.

## 3. Warehouse Web App & Sound Synthesis

- [x] 3.1 Create `/pack` full-screen responsive warehouse web application (`whatnot_else/www/pack.html`, `pack.js`, `pack.css`) with high-visibility dark mode UI and barcode autofocus.
- [x] 3.2 Implement client-side Web Audio API oscillator tone generator (success chime, error alarm) and Web Speech API synthesizer for spoken tray announcements (e.g. "Tray 14 - Collector Dan").
- [x] 3.3 Implement dual-mode toggle in `/pack` for **Scan-to-Tray** (sorting) and **Scan-to-Box** (packing audit) with live verification progress bars.

## 4. Testing & Verification

- [x] 4.1 Write Python unit tests in `test_fulfillment_tray.py` verifying tray allocation, multi-item sorting, wrong-item rejection, and weight advisor calculations.
- [x] 4.2 Verify Python syntax across all new controllers and validate JSON schemas.

## 5. Git Lifecycle & Deployment

- [x] 5.1 Create git feature branch `feat/scan-to-tray-fulfillment-and-collectibles`.
- [x] 5.2 Commit changes with Conventional Commits message and comprehensive description.
- [x] 5.3 Push feature branch to origin.
- [x] 5.4 Create GitHub Pull Request with full context, test verification, and impact analysis.
- [x] 5.5 Merge Pull Request into `main` using admin override (`gh pr merge --admin`).
- [x] 5.6 Run automated post-merge verification.
- [x] 5.7 Validate K3S manifests and build container image.
