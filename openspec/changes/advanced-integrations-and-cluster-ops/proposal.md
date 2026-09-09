## Why

To bring WhatnotElse to full enterprise completion across Phase 2 and Phase 3 specifications, we must deliver the remaining integration clients, notifications engine, advanced AI forecasting, and Kubernetes cluster operational workflows (site initialization job and backup cronjob). This closes all pending loops: Whatnot GraphQL API client readiness, Twilio SMS order alerts, AI demand and pricing forecasting, automated cluster provisioning (`site-init-job.yaml`), and MariaDB backup CronJobs.

## What Changes

- **Whatnot GraphQL Client (`whatnot_else/api/whatnot_client.py`)**:
  - Production-ready GraphQL client architecture ready to communicate with Whatnot Developer API upon OAuth bearer token grant, supporting queries (`getOrders`, `getInventory`, `getLivestreams`) and mutations (`updateListingPrice`, `cancelOrder`).
- **Notifications & SMS Engine (`whatnot_else/api/notifications.py`)**:
  - Twilio SMS and email dispatchers for order confirmations, shipping updates, and low-inventory restock alerts.
- **Advanced AI: Demand Forecasting & Price Optimization (`whatnot_else/api/forecasting.py`)**:
  - Historical sales analyzer predicting sell-through rates and optimal starting auction bids based on category, condition, and market velocity using Gemini API.
- **Role & Security Fixtures**:
  - Define custom roles: `Whatnot Admin`, `Whatnot Seller`, `Whatnot Warehouse Staff`, `Whatnot Accountant` in `whatnot_else/fixtures/role.json`.
- **K3S Cluster Operations Manifests (`k8s/`)**:
  - `k8s/site-init-job.yaml`: Automated one-time setup job executing `bench new-site`, installing `erpnext` and `whatnot_else`.
  - `k8s/mariadb-backup-cronjob.yaml`: Automated daily Longhorn/MariaDB dump backup CronJob.
  - `k8s/pdb.yaml`: PodDisruptionBudget for high availability.

## Whatnot Impact

The platform reaches complete enterprise maturity. When Whatnot grants production API credentials, sellers can toggle direct GraphQL sync with zero code changes. Streamers receive SMS notifications when a Whale VIP buyer places an order, and AI suggests data-driven starting bids for maximum auction velocity.

## Affected Modules, DocTypes & Frappe Hooks

- **Modules**: `ai-features`, `fulfillment`, `infra`, `security`
- **Manifests**: `k8s/site-init-job.yaml`, `k8s/mariadb-backup-cronjob.yaml`, `k8s/pdb.yaml`

## Rollback Plan

Integrations are modular; removing the manifests or API files leaves core inventory and orders completely intact.

## Capabilities

### New Capabilities
- `whatnot-graphql-client`: Whatnot GraphQL API client for queries and mutations.
- `notifications-engine`: SMS (Twilio) and email dispatch for order alerts.
- `ai-demand-forecasting`: Predictive starting bid and price recommendation engine.
- `cluster-operations`: Kubernetes site initialization job, PodDisruptionBudget, and automated backup CronJob.

### Modified Capabilities
<!-- None -->

## Impact

- **Codebase**: Adds GraphQL client, forecasting engine, notification module, fixtures, and K3S manifests.
