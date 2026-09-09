# WhatnotElse 🚀

> **Enterprise-grade multi-tenant ERP platform for Whatnot sellers**, built on top of [Frappe](https://frappeframework.com/) and [ERPNext v16](https://erpnext.com/), designed for local high-availability deployment on K3S Kubernetes.

[![Frappe Framework](https://img.shields.io/badge/Frappe-v16-blue.svg)](https://frappeframework.com/)
[![ERPNext](https://img.shields.io/badge/ERPNext-v16-blue.svg)](https://erpnext.com/)
[![Kubernetes](https://img.shields.io/badge/K3S-Cluster-326ce5.svg)](https://k3s.io/)
[![OpenSpec](https://img.shields.io/badge/OpenSpec-v1.5.0-success.svg)](https://github.com/openspec-org/openspec)

---

## 🌟 Overview

**WhatnotElse** transforms Whatnot live selling into a fully professional, automated e-commerce and logistics enterprise. It bridges live streaming auctions and Buy-It-Now (BIN) sales with enterprise inventory, accounting, warehouse sorting, and predictive AI analytics.

Each seller operates under a dedicated wildcard subdomain:
```
https://<seller>.whatnotelse.com
```

---

## 📦 Core Modules & Capabilities

1. **📦 Inventory Management & Collectibles Vault**
   - Centralized SKU catalog, real-time quantity tracking, and batch CSV imports.
   - Cost of Goods Sold (COGS) tracking and mobile QR/barcode scanning lookup.
   - **Graded Collectibles Vault**: Dedicated slab certification tracking for PSA, BGS, CGC, SGC, PCGS, and NGC, including grade numbers, cert numbers, and population notes.

2. **🎬 Live Show Planner**
   - Stream scheduling with custom calendar and visual Kanban status views.
   - Run-of-show broadcast staging sheets and live item assignment.
   - Stream go-live lifecycle management and profit analysis per broadcast.

3. **🛒 Order Management**
   - Seamless ingestion of Whatnot orders via CSV and GraphQL webhooks (`Listing`, `Order`, `Livestream`).
   - Automatic generation of ERPNext Sales Orders, invoices, and delivery notes.
   - Direct linking of orders to designated warehouse sorting bins.

4. **🚚 Fulfillment, Tray Sorting & Packing Verifier**
   - **Scan-to-Tray Sorting Mode**: Auto-partitions live show buyers into physical warehouse trays (Trays 1–150); scanning sold items triggers real-time visual routing and spoken audio cues (`"Tray 14 - Collector Dan"`).
   - **Scan-to-Box Packing Verifier**: Audits items scanned into boxes against tray manifests. Instantly fires **Mis-Ship Alarms** (audio buzzer + visual modal) if an item belongs in another buyer's tray.
   - **Web Audio Sound Synthesis**: In-browser oscillator sound generator and Web Speech API synthesis—zero external audio file dependencies.
   - **Combined Parcel Weight Advisor**: Automatically sums order item weights and warns sellers when multi-lot shipments exceed the USPS 16 oz Ground Advantage threshold.
   - 4x6 Zebra/DYMO thermal packing slip and label integration.

5. **📱 Front-End Web Applications & PWA**
   - **`/scanner`**: Full-screen, responsive camera barcode/QR scanner web app with dark mode aesthetics and instant live show item allocation.
   - **`/pack`**: High-contrast warehouse fulfillment station with oversized typography (visible from 6+ feet) for packing benches.
   - **PWA Ready**: Web app manifest and service worker caching for offline resilience.

6. **💰 Financials & P&L**
   - Exact net margin calculation accounting for Whatnot platform commissions (~11%), payment processing fees, and COGS.
   - Stripe payout batch reconciliation and automated 1099-K tax reporting.
   - Script Reports: *Whatnot Show Profitability* & *Whatnot Item Margin Analysis*.

7. **👥 Customer & VIP CRM**
   - Repeat buyer tracking, Lifetime Value (LTV), notes, and VIP tiers (Bronze, Silver, Gold, Platinum VIP).
   - Buyer transaction history and giveaway claim monitoring.

8. **📥 Sourcing & Purchasing Intake**
   - Purchase Orders for bulk inventory, vendor management, and sourcing batch intake (`Whatnot Sourcing Batch`) with weighted or equal unit COGS allocation.

9. **🔄 Multi-Platform Sync**
   - Cross-listing synchronization (`Whatnot Channel Bridge`, `Whatnot Cross Listing`) across eBay, Shopify, and Mercari.
   - HMAC-SHA256 authenticated webhook listener with asynchronous delisting dispatcher to eliminate double-selling.

10. **🤖 AI Intelligence & Automation**
    - Google Gemini API integration for automated title copywriting, markdown description formatting, and auction starting bid / reserve optimization.
    - Local privacy-first LLM inference via Ollama running on in-cluster GPU nodes.
    - Transactional Twilio SMS engine for high-priority order and restock notifications.

11. **📊 Executive Command Center**
    - Custom Frappe Desk executive analytics page (`/app/whatnot-dashboard`) displaying Gross GMV, Net Payouts, Active Inventory COGS, VIP buyer leaderboards, and category breakdown charts.

---

## 🏗️ Architecture & Infrastructure

- **Target Deployment**: Local K3S Kubernetes Cluster (`whatnot-else` namespace).
- **Ingress & Networking**: Traefik Gateway API (`kube-system/cluster-gateway`) HTTPRoute on VIP `192.168.4.7`.
- **DNS & TLS**: Wildcard DNS (`*.whatnotelse.com`) + cert-manager Cloudflare DNS-01 ACME issuer.
- **Storage**: Longhorn RWX storage for Frappe sites and RWO for MariaDB.
- **Container Registry**: Local private registry `registry.maddscientist.com`.
- **Node Affinity**: Excludes `node05` (GPU-only taint) for general application pods.
- **High Availability**: PodDisruptionBudgets (`pdb.yaml`), automated MariaDB backup cronjobs (`mariadb-backup-cronjob.yaml`), and site initialization job (`site-init-job.yaml`).

---

## 🔄 Commit, PR & Deployment Lifecycle

All code changes in this repository strictly adhere to the OpenSpec-driven workflow:

```text
[ Feature Branch ] ──► [ Well-Documented Commit ] ──► [ Push Remote ]
                                                              │
                                                              ▼
[ K3S Deployment ] ◄── [ Post-Merge Checks ] ◄── [ PR & Merge (--admin) ]
```

1. **Branch**: Create a focused branch from `main` (`feature/...` or `fix/...`). Never commit directly to `main`.
2. **Commit**: Write conventional commits with descriptive bodies detailing architectural impact and affected DocTypes.
3. **Push**: Push branch to GitHub remote origin.
4. **PR**: Open a pull request detailing context, changes, testing performed, and risk analysis.
5. **Merge**: Require CI checks to pass. Merge with admin privileges (`--admin`) to bypass approvals when operating as sole maintainer.
6. **Post-Merge**: Monitor automated post-merge test verification.
7. **Deploy**: Build multi-arch container, push to `registry.maddscientist.com`, and apply Kubernetes manifests to the K3S cluster.

---

## 🛠️ OpenSpec Specifications

This project is engineered using **OpenSpec**. Full specifications, design documents, and module boundaries are cataloged under:
```
openspec/
├── config.yaml
├── project.md
└── specs/
    ├── inventory/
    ├── live-shows/
    ├── orders/
    ├── fulfillment/
    ├── tray-sorting-workflow/
    ├── scan-to-box-verifier/
    ├── financials/
    ├── crm/
    ├── purchasing/
    ├── multi-platform/
    ├── ai-features/
    ├── analytics/
    ├── infra/
    └── security/
```

---

## 📄 License
Private & Proprietary. All rights reserved.
