## Context

Sellers operate across dual contexts: desk workstations for inventory intake, and smartphones during live auctions and warehouse staging. Providing a dedicated dashboard custom page within Frappe Desk combined with PWA installability elevates WhatnotElse into a polished, professional enterprise suite.

## Goals / Non-Goals

**Goals:**
- Implement Frappe custom page `whatnot_dashboard` featuring responsive KPI metric counters and charts.
- Implement server-side aggregation in `whatnot_else/api/analytics.py`.
- Add PWA `manifest.json` and service worker `sw.js` enabling "Add to Home Screen" on iOS Safari and Android Chrome.

**Non-Goals:**
- Native App Store release (PWA meets all mobile requirements with zero app store review overhead).
