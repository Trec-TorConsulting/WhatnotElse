## Context

High-volume live selling on Whatnot generates bursts of auction sales where buyers regularly purchase 5–20 items across a single 2-to-4 hour stream. Post-show fulfillment becomes chaotic without physical sorting infrastructure. Standalone competitors like Scan2Tray solve this by mapping buyers to physical tray bins, but leave sellers isolated from ERP inventory, financials, and CRM.

This design introduces native physical fulfillment tray management (`Whatnot Fulfillment Tray`), a high-throughput warehouse web app (`/pack`) supporting **Scan-to-Tray** (sorting) and **Scan-to-Box** (audit & packing), Web Audio / Web Speech API sound cues, combined weight advising, and collectible slab/card grading tracking.

## Goals / Non-Goals

**Goals:**
- Provide dynamic tray allocation: Automatically partition a live show's buyers into numbered trays (1 to N).
- High-speed Scan-to-Tray sorting: Item scan immediately announces the tray number via synthesized voice and chimes, with large full-screen visual routing cards.
- Mis-ship elimination with Scan-to-Box: Verifying items scanned into the box against expected tray contents; trigger immediate error buzzers for discrepancies.
- Combined weight & rate advisor: Tally cumulative parcel weight and warn if package exceeds USPS tier thresholds.
- Collectible grading metadata: Track PSA, BGS, CGC, SGC grades and cert numbers on `Whatnot Item`.

**Non-Goals:**
- Automated conveyor or robotic bin diverter hardware integration (reserved for enterprise warehouse phase).
- Third-party web scraping of PSA/CGC websites without official API credentials.

## Architecture & Data Flow

```
[ Whatnot Live Show Concluded ]
               │
               ▼
[ API: allocate_show_trays ] ──► Creates / Assigns `Whatnot Fulfillment Tray` (Tray 1..N per Buyer)
               │
               ▼
   [ Mode 1: Scan-to-Tray ]  (Warehouse Operator sorts loose items)
   - Scan Item Barcode
   - Server resolves item -> Tray #
   - UI: Web Speech "Tray 14" + High-pitch chime + Large Visual Display
   - Item status marked "Sorted"
               │
               ▼
   [ Mode 2: Scan-to-Box ]   (Packer boxes up Tray 14)
   - Scan Tray #14
   - UI loads expected item checklist & combined parcel weight
   - Scan each item into box:
       ├── Correct item: Success chime + checkmark
       └── Wrong item: Loud Alarm Buzzer + Haptic + Red Warning
   - When 100% packed: "Print 4x6 Label & Packing Slip"
```

## Decisions

### Decision 1: Dedicated `Whatnot Fulfillment Tray` DocType
- **Rationale**: Modeling trays as a dedicated DocType allows tracking physical bins (1–150), re-using bins across shows, managing tray lifecycles (`Available`, `Allocated`, `Sorting`, `Ready to Pack`, `Packed`, `Shipped`), and auditing packed timestamps.
- **Alternatives Considered**: Storing tray numbers solely as a column on `Whatnot Order`. Discarded because multi-item orders and multi-order buyers in the same show require a single consolidated bin entity.

### Decision 2: Native Web Audio API & SpeechSynthesis for Audio Guidance
- **Rationale**: Warehouse environments demand rapid auditory cues without lag. Using the browser's native `AudioContext` (oscillator frequency sweeps for chimes and alarms) and `window.speechSynthesis` ensures zero network latency, zero external audio asset hosting, and offline PWA reliability.
- **Alternatives Considered**: Loading MP3/WAV files. Discarded due to potential caching issues, asset download delays, and inability to dynamically speak dynamic tray numbers.

### Decision 3: Dedicated `/pack` Web Page UI
- **Rationale**: Packers on warehouse benches need high-contrast dark mode, oversized typography readable from 4 feet away, persistent barcode input autofocus, and one-tap mode switching between sorting and boxing.
- **Alternatives Considered**: Packing inside standard Frappe Desk form views. Discarded because standard form views have too much visual clutter and do not support fast hands-free scanning workflows.

## Risks / Trade-offs

- **[Browser Audio Autoplay Restrictions]** → Browsers require a user interaction before allowing audio playback.
  - *Mitigation*: The `/pack` interface presents a prominent "Start Fulfillment Station" audio activation button on initial load that unlocks the `AudioContext`.
- **[Show with >150 Unique Buyers exceeding physical rack capacity]** → Small warehouses may only have 50 or 100 physical bins.
  - *Mitigation*: The tray allocation algorithm allows specifying max available trays and batches buyers into waves (e.g. Wave 1: Trays 1–50, Wave 2: Trays 1–50).

## Migration Plan

1. Create DocType `Whatnot Fulfillment Tray` and child table `Whatnot Fulfillment Tray Item`.
2. Add custom fields to `Whatnot Item` (`is_graded`, `grading_company`, `grade`, `cert_number`).
3. Add custom field `fulfillment_tray` to `Whatnot Order`.
4. Deploy `/pack` web page and backend fulfillment API module `whatnot_else.api.fulfillment`.
5. Rollback: If rolled back, removing the `/pack` web page and unlinking `fulfillment_tray` leaves orders, items, and previous shows completely intact.
