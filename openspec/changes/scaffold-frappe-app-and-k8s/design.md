## Context

WhatnotElse is architected as an enterprise custom Frappe app (`whatnot_else`) running on Frappe Framework v16 / ERPNext v16, deployed in a dedicated `whatnot-else` namespace on a local K3S cluster. The cluster uses Traefik Gateway API on VIP `192.168.4.7` with cert-manager Cloudflare DNS-01 ACME issuer for wildcard TLS certificate generation (`*.whatnotelse.com`).

While Whatnot's developer GraphQL API is in restricted private preview, Phase 1 establishes the operational core through structured CSV imports from Whatnot Seller Hub (orders and inventory ledgers), native ERPNext sales order synchronization, live show planning, and dual AI integration (cloud Gemini API + private in-cluster Ollama LLM).

## Goals / Non-Goals

**Goals:**
- Scaffold the production `whatnot_else` Frappe application structure adhering to Frappe v16 packaging standards.
- Model and generate the core DocTypes: `Whatnot Seller Profile`, `Whatnot Item`, `Whatnot Show`, `Whatnot Show Item`, `Whatnot Order`, and `Whatnot Order Item`.
- Build CSV ingestion controllers with schema validation, currency/fee calculation, and automated ERPNext Sales Order/Delivery Note linkage.
- Integrate AI copywriting assistance using Google Generative AI (Gemini) with fallback/local capability to Ollama.
- Provide production-ready Kubernetes manifests in `k8s/` configured for Traefik HTTPRoute wildcard routing, Longhorn storage, MariaDB, Redis, and multi-worker Frappe topology.
- Provide a reproducible local Docker buildx setup pushing to `registry.maddscientist.com/whatnot-else/erpnext-whatnot:latest`.

**Non-Goals:**
- Direct Whatnot GraphQL webhooks in Phase 1 (reserved for Phase 2 upon access approval by Whatnot).
- Native automated label generation via USPS Web Tools API directly (Phase 1 leverages Whatnot's pre-paid bulk label generation workflow and tracking number import).
- Public multi-tenant self-service registration (Phase 1 uses admin-provisioned seller profiles and subdomains).

## Decisions

### 1. Frappe v16 App Architecture
- **Choice**: Standard standalone Frappe app with module name `whatnot_else`.
- **Rationale**: Keeps custom logic decoupled from ERPNext core upgrades. Standard hooks (`doctype_js`, `doc_events`, `override_whitelisted_methods`) allow non-destructive extensions to ERPNext's `Item`, `Sales Order`, and `Customer`.
- **Alternatives Considered**: Modifying ERPNext directly via fixtures or scripts (rejected: brittle and hinders upstream upgrades).

### 2. CSV Ingestion Engine Design
- **Choice**: Idempotent batch parser with transaction rollback per row and deduplication based on Whatnot Order ID / Barcode.
- **Rationale**: Whatnot sellers export CSV ledgers frequently; the importer must avoid creating duplicate sales orders or skewed COGS figures when files are re-uploaded.
- **Alternatives Considered**: Direct SQL raw inserts (rejected: bypasses Frappe validation hooks and ERPNext GL entry generation).

### 3. Ingress & Routing via Traefik Gateway API
- **Choice**: Traefik Gateway API `HTTPRoute` referencing `kube-system/cluster-gateway` on VIP `192.168.4.7`. Hostnames matched: `whatnotelse.com` and wildcard `*.whatnotelse.com`.
- **Rationale**: Complies with cluster architecture guidelines; replaces deprecated Ingress/IngressRoute with modern Kubernetes Gateway API standards.
- **Alternatives Considered**: Legacy Traefik IngressRoute (rejected: deprecated in the target homelab environment).

### 4. Secret & Environment Variable Management
- **Choice**: Kubernetes Secret `whatnot-else-secrets` providing `GEMINI_API_KEY`, DB root password, and Frappe encryption key. No secret keys stored in source control.
- **Rationale**: Adheres to strict zero-secret git policy and cluster security rules.

### 5. Node Affinity & Workload Placement
- **Choice**: Universal node anti-affinity excluding `node05` (tainted for GPU-only workloads) for all application, web, and database pods.
- **Rationale**: Prevents CPU-bound Frappe workers or MariaDB from consuming high-value GPU memory on `node05`.

## Risks / Trade-offs

- **[Risk] Whatnot Seller Hub CSV Format Changes** → *Mitigation*: Importer implements header mapping detection and field normalization. If Whatnot modifies column headers, mappings can be updated in `Whatnot Seller Profile` without code modifications.
- **[Risk] Multi-Tenant Subdomain Routing Complexity** → *Mitigation*: Frappe's native multi-tenant site resolution (`bench config dns_multitenant on`) dynamically matches Host headers directly to site directories or resolves via common site config.
- **[Risk] Database Migration Locks During Upgrades** → *Mitigation*: Longhorn snapshots are scheduled prior to migrations; Frappe patches run sequentially in an init container before traffic routes to web workers.

## Migration Plan

1. Scaffold app structure and verify Python syntax and DocType schemas.
2. Build container image via Docker buildx and push to `registry.maddscientist.com`.
3. Apply Kubernetes manifests to `whatnot-else` namespace.
4. Execute `bench new-site` or initialize site database with ERPNext and `whatnot_else` installed.
5. In case of failure: roll back K8s deployment to previous image tag and restore Longhorn volume snapshot.
