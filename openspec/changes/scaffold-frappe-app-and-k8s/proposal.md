## Why

Whatnot live sellers currently manage inventory, scheduled stream shows, order fulfillment, and financial accounting through disparate spreadsheets and manual processes. To establish WhatnotElse as a production-ready, enterprise-grade ERP platform, we must scaffold the foundational Frappe custom app (`whatnot_else`), establish core data models (DocTypes), implement the CSV ingestion pipeline for Whatnot Seller Hub exports, and deliver production K3S Kubernetes deployment manifests with multi-tenant wildcard routing (`*.whatnotelse.com`).

## What Changes

- **Frappe App Scaffold**: Initialize `whatnot_else` Frappe application structure (`pyproject.toml`, `setup.py`, `hooks.py`, `modules.txt`, license, app config).
- **Core DocTypes**:
  - `Whatnot Seller Profile`: Multi-seller account credentials, shop slug (`<seller>`), CSV mapping profiles, and API tokens.
  - `Whatnot Item`: Master inventory catalog with SKUs, barcode/QR codes, COGS, condition, and category mappings.
  - `Whatnot Show`: Stream planner for scheduling live broadcasts, assigning auction/BIN items, and tracking show status.
  - `Whatnot Show Item`: Child DocType linking catalog items to scheduled shows with start prices and reserve bids.
  - `Whatnot Order`: Whatnot orders mapped to ERPNext sales records, tracking buyer usernames, shipment IDs, and fee deductions.
  - `Whatnot Order Item`: Child DocType recording line items, sold prices, and associated show IDs.
- **CSV Ingestion Engine**: Python controller in `whatnot_else/api/importers.py` to ingest and validate Whatnot Seller Hub CSV exports (Orders and Inventory).
- **AI Intelligence Helper**: Integration module supporting Google Gemini API (via `GEMINI_API_KEY` K8s secret) and local Ollama endpoint (`http://ollama.ollama.svc.cluster.local:11434`) for listing title and description optimization.
- **Containerization**: Multi-arch `Dockerfile` based on `frappe/erpnext:version-16` installing `whatnot_else`, built and pushed to `registry.maddscientist.com/whatnot-else/erpnext-whatnot:latest`.
- **K3S Kubernetes Deployment**: Full manifest suite under `k8s/` implementing Traefik Gateway API HTTPRoute for `*.whatnotelse.com` and `whatnotelse.com`, cert-manager Cloudflare DNS-01 certificate, Longhorn PVCs, MariaDB 10.6 StatefulSet, Redis cache/queue/socketio, and Frappe worker deployments with node05 (GPU) affinity exclusion.

## Whatnot Impact

Whatnot sellers gain an automated central command center. Instead of manually re-entering auction sales into accounting spreadsheets, sellers upload their Whatnot Seller Hub CSV or run automated intake to generate real-time COGS, net profit calculations (factoring in the ~11% Whatnot take rate), packing slips, and cross-show inventory balances.

## Affected Modules, DocTypes & Frappe Hooks

- **Modules**: `inventory`, `live-shows`, `orders`, `fulfillment`, `financials`, `ai-features`, `infra`
- **DocTypes**:
  - `Whatnot Seller Profile`
  - `Whatnot Item`
  - `Whatnot Show`
  - `Whatnot Show Item`
  - `Whatnot Order`
  - `Whatnot Order Item`
- **Frappe Hooks**: `app_name`, `app_title`, `app_publisher`, `app_description`, `doc_events` (sync order to ERPNext Sales Order), `scheduled_tasks`
- **K3S Manifests**: `k8s/namespace.yaml`, `k8s/secret.template.yaml`, `k8s/configmap.yaml`, `k8s/pvc.yaml`, `k8s/mariadb.yaml`, `k8s/redis.yaml`, `k8s/frappe.yaml`, `k8s/gateway.yaml`, `k8s/certificate.yaml`

## Rollback Plan

All DocTypes are modular custom schema additions managed through Frappe bench migrations. Rolling back involves:
1. `bench uninstall-app whatnot_else` to remove custom tables and links without destroying base ERPNext core records.
2. In Kubernetes: Reverting deployment image tag to previous release or scaling deployments to 0. Database volumes on Longhorn maintain automatic snapshots prior to major schema updates.

## Capabilities

### New Capabilities
- `app-scaffold`: Foundation Frappe custom app structure, configuration, dependencies, and packaging.
- `inventory-management`: Core item catalog, SKU tracking, COGS, category classification, and barcode/QR metadata.
- `live-show-planner`: Stream scheduling, item staging, show status lifecycle, and auction item allocation.
- `order-ingestion`: Whatnot Seller Hub CSV parsing, order validation, and automated ERPNext Sales Order generation.
- `k8s-deployment`: Production K3S infrastructure manifests, Gateway API wildcard routing, cert-manager TLS, and MariaDB/Redis stateful workloads.

### Modified Capabilities
<!-- None: Initial implementation of baseline specifications -->

## Impact

- **Codebase**: Creates `/whatnot_else` app directory, configuration files, DocType schemas, and Python controllers.
- **Infrastructure**: Creates deployable Kubernetes manifests in `k8s/` targeting `whatnot-else` namespace in K3S homelab cluster.
- **Dependencies**: Adds `frappe` and `erpnext` Python runtime dependencies and Google generative AI client library.
