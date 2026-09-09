## 1. Frappe Custom App Foundation (whatnot_else)

- [x] 1.1 Scaffold `whatnot_else` package root files (`pyproject.toml`, `setup.py`, `requirements.txt`, `MANIFEST.in`, `license.txt`)
- [x] 1.2 Scaffold Frappe module files (`whatnot_else/__init__.py`, `whatnot_else/hooks.py`, `whatnot_else/modules.txt`, `whatnot_else/patches.txt`)
- [x] 1.3 Create module descriptor directory `whatnot_else/whatnot_else/__init__.py`

## 2. Core DocTypes Implementation

- [x] 2.1 Implement `Whatnot Seller Profile` DocType (JSON schema and Python controller)
- [x] 2.2 Implement `Whatnot Item` DocType with SKU, COGS, category, and barcode tracking
- [x] 2.3 Implement `Whatnot Show` DocType with stream lifecycle statuses and calendar view hooks
- [x] 2.4 Implement `Whatnot Show Item` child DocType for show allocation and start/reserve bidding
- [x] 2.5 Implement `Whatnot Order` DocType with fee calculations and tracking numbers
- [x] 2.6 Implement `Whatnot Order Item` child DocType for order line item breakdowns

## 3. CSV Ingestion Engine & Integrations

- [x] 3.1 Implement Whatnot Seller Hub orders CSV parser in `whatnot_else/api/importers.py`
- [x] 3.2 Implement Whatnot inventory ledger CSV parser in `whatnot_else/api/importers.py`
- [x] 3.3 Implement AI listing generator in `whatnot_else/api/ai.py` supporting Gemini API and local Ollama
- [x] 3.4 Implement mobile barcode lookup endpoint in `whatnot_else/api/lookup.py`

## 4. Containerization & Build Configuration

- [x] 4.1 Create multi-stage `Dockerfile` based on `frappe/erpnext:version-16` installing `whatnot_else`
- [x] 4.2 Create container build & push script `build-image.sh` for `registry.maddscientist.com/whatnot-else/erpnext-whatnot:latest`

## 5. K3S Kubernetes Infrastructure Manifests

- [x] 5.1 Create `k8s/namespace.yaml` for `whatnot-else` namespace
- [x] 5.2 Create `k8s/secret.template.yaml` for database and `GEMINI_API_KEY` credentials
- [x] 5.3 Create `k8s/configmap.yaml` for common site configuration
- [x] 5.4 Create `k8s/pvc.yaml` for Longhorn RWX sites and RWO database volumes
- [x] 5.5 Create `k8s/mariadb.yaml` StatefulSet with node05 anti-affinity
- [x] 5.6 Create `k8s/redis.yaml` Deployments for cache, queue, and socketio
- [x] 5.7 Create `k8s/frappe.yaml` Deployments for python web, workers (default/short/long), and scheduler
- [x] 5.8 Create `k8s/gateway.yaml` Traefik Gateway HTTPRoute for `whatnotelse.com` and `*.whatnotelse.com`
- [x] 5.9 Create `k8s/certificate.yaml` cert-manager Certificate with Cloudflare DNS-01 issuer

## 6. Verification and Git Lifecycle Operations

- [x] 6.1 Validate Python syntax and DocType JSON validity
- [x] 6.2 Validate Kubernetes manifest YAML syntax
- [ ] 6.3 Execute Lifecycle Branch & Commit: Create feature branch `feature/scaffold-app-and-k8s`, commit with Conventional Commits, push, and open PR
