# WhatnotElse 🚀

> **Enterprise-grade multi-tenant ERP platform for Whatnot sellers**, built on top of [Frappe](https://frappeframework.com/) and [ERPNext v16](https://erpnext.com/), designed for local high-availability deployment on K3S Kubernetes.

[![Frappe Framework](https://img.shields.io/badge/Frappe-v16-blue.svg)](https://frappeframework.com/)
[![ERPNext](https://img.shields.io/badge/ERPNext-v16-blue.svg)](https://erpnext.com/)
[![Kubernetes](https://img.shields.io/badge/K3S-Cluster-326ce5.svg)](https://k3s.io/)
[![OpenSpec](https://img.shields.io/badge/OpenSpec-v1.5.0-success.svg)](https://github.com/openspec-org/openspec)

---

## 🌟 Overview

**WhatnotElse** transforms Whatnot live selling into a fully professional, automated e-commerce and logistics enterprise. It bridges live streaming auctions and Buy-It-Now (BIN) sales with enterprise inventory, accounting, fulfillment, and predictive AI analytics.

Each seller operates under a dedicated subdomain:
```
https://<seller>.whatnotelse.com
```

---

## 📦 Core Modules

1. **📦 Inventory Management**
   - Centralized SKU catalog, real-time quantity tracking, and batch CSV imports.
   - Cost of Goods Sold (COGS) tracking and QR/barcode scanning lookup on mobile.
2. **🎬 Live Show Planner**
   - Stream planning, scheduling, item allocation, and run-of-show staging.
   - Live stream performance metrics and profit analysis per broadcast.
3. **🛒 Order Management**
   - Seamless ingestion of Whatnot orders via CSV / GraphQL webhooks.
   - Automatic creation of ERPNext Sales Orders, invoices, and delivery notes.
4. **🚚 Fulfillment & Shipping**
   - Integration with Whatnot's built-in USPS label generation and bulk packing workflows.
   - Zebra / DYMO thermal label printing and customized packing slips.
5. **💰 Financials & P&L**
   - Exact net margin calculation accounting for Whatnot platform fees (~11%), processing fees, and COGS.
   - Stripe payout reconciliation and tax/1099 compliance tracking.
6. **👥 Customer & VIP CRM**
   - Repeat buyer intelligence, lifetime value (LTV), buyer notes, and VIP status tiers.
7. **📥 Sourcing & Purchasing**
   - Purchase Orders for bulk inventory, vendor management, and flea market / estate sale sourcing intake.
8. **🔄 Multi-Platform Sync**
   - Cross-listing synchronization between Whatnot, eBay, Shopify, and Mercari to avoid double-selling.
9. **🤖 AI Intelligence (Gemini + Local Ollama)**
   - Gemini API integration for automated title and description copywriting, keyword optimization, and pricing suggestions.
   - Local privacy-first LLM inference via Ollama running in-cluster on NVIDIA GPU nodes.
10. **📊 Reporting & Analytics**
    - Executive dashboards for top categories, sell-through velocity, and broadcast ROI.

---

## 🏗️ Architecture & Infrastructure

- **Target Deployment**: Local K3S Kubernetes Cluster (`whatnot-else` namespace).
- **Ingress & Networking**: Traefik Gateway API (`kube-system/cluster-gateway`) on VIP `192.168.4.7`.
- **DNS & TLS**: Wildcard DNS (`*.whatnotelse.com`) + cert-manager Cloudflare DNS-01 ACME issuer.
- **Storage**: Longhorn RWX storage for Frappe sites and RWO for MariaDB.
- **Container Registry**: Local private registry `registry.maddscientist.com`.
- **Node Affinity**: Excludes `node05` (GPU-only taint) for general application pods.

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

## 🛠️ Getting Started

### Prerequisites
- Docker Engine / Docker Buildx
- Git & GitHub CLI (`gh`)
- Kubernetes CLI (`kubectl`)
- Python 3.11+

### OpenSpec Specifications
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
