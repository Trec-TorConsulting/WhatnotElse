## Why

Sellers need a unified executive overview of their live operations, sell-through velocity, revenue trends, top items, and live broadcast performance without clicking through multiple reports. Furthermore, to make the mobile scanner and desk interface operate as a seamless application on iPhones and Android devices, we must deliver a responsive Seller Analytics Dashboard custom page and PWA (Progressive Web App) manifest with offline caching and home screen install capability.

## What Changes

- **Executive Seller Analytics Dashboard (Frappe Custom Page)**:
  - Custom Desk Page `/app/whatnot-dashboard` in `whatnot_else/whatnot_else/page/whatnot_dashboard/` with dark mode executive UI.
  - KPI cards: 30-Day Gross Revenue, Total Net Profit, Avg Sell-Through Rate %, Active VIP Buyers count.
  - Interactive charts: Daily Gross vs. Net Profit curve, Revenue by Product Category donut, and Upcoming Live Broadcasts schedule.
  - Backend telemetry aggregator `get_dashboard_analytics` in `whatnot_else/api/analytics.py`.
- **Progressive Web App (PWA) Capabilities**:
  - Web App Manifest `manifest.json` under `whatnot_else/public/manifest.json`.
  - Service Worker `sw.js` for offline caching of scanner assets and instant load times.
  - Web app icons and mobile viewport meta headers.

## Whatnot Impact

Sellers can install WhatnotElse onto their phone home screens like a native app. At a single glance from their phone or studio laptop, sellers see their broadcast ROI, inventory velocity, and upcoming stream schedule.

## Affected Modules, DocTypes & Frappe Hooks

- **Modules**: `analytics`, `live-shows`, `orders`
- **Pages**: `whatnot-dashboard`
- **Hooks**: `add_to_apps_screen` and web asset links

## Rollback Plan

Custom page and PWA manifest can be removed without touching stored database records.

## Capabilities

### New Capabilities
- `seller-dashboard`: Executive analytics dashboard page with real-time KPI metrics and charts.
- `pwa-capabilities`: Progressive Web App manifest and service worker for mobile installation.

### Modified Capabilities
<!-- None: Initial implementation of analytics dashboard -->

## Impact

- **Codebase**: Adds Frappe page files and `whatnot_else/api/analytics.py`.
