# Spec: Infrastructure — whatnot-else K3S Namespace

## Capability
Deploy a fully isolated Frappe/ERPNext v16 instance in the `whatnot-else` K3S namespace,
accessible at whatnotelse.com, following all HomeLab-Redo cluster conventions.

## Requirements

### Requirement: Isolated namespace
- Namespace `whatnot-else` with no shared workloads from `frappe` namespace
- Own MariaDB StatefulSet, own Redis instances, own Frappe workers

### Requirement: Gateway API routing
- HTTPRoute on `kube-system/cluster-gateway` matching `*.whatnotelse.com` and `whatnotelse.com`
- Wildcard DNS `*.whatnotelse.com` and root `whatnotelse.com` routed to VIP `192.168.4.7`
- ReferenceGrant allowing kube-system gateway to route to `whatnot-else` namespace
- Traefik middleware to pass seller host header (`X-Forwarded-Host`)
- No legacy Ingress or IngressRoute objects

### Requirement: TLS via cert-manager
- cert-manager Certificate for `*.whatnotelse.com` and `whatnotelse.com` using Cloudflare DNS-01 solver (required for wildcards)
- Certificate Secret referenced by Gateway HTTPS listener

### Requirement: Longhorn storage
- PVC `whatnot-sites` — RWX, 20Gi, Longhorn StorageClass
- PVC `whatnot-mariadb` — RWO, 50Gi, Longhorn StorageClass

### Requirement: Node scheduling
- All pods MUST exclude node05 (gpu-only taint)
- nodeAffinity NotIn: ["node05"]

### Requirement: Multi-arch image
- Custom image: registry.maddscientist.com/whatnot-else/erpnext-whatnot:latest
- Built for linux/arm64 (RPi 5 nodes) and linux/amd64 (Intel mini PC nodes)

### Requirement: Secret management
- All credentials in Kubernetes Secrets
- secret.yaml in repo is a template with placeholder values only
- Never commit real credentials to git

## Scenarios

### Scenario: App is reachable
- WHEN a user navigates to https://whatnotelse.com
- THEN the Frappe login page loads
- AND TLS is valid (browser shows padlock)

### Scenario: MariaDB survives pod restart
- WHEN the MariaDB pod is deleted
- THEN it restarts and data is intact from Longhorn PVC

### Scenario: Node05 excluded
- WHEN cluster schedules any whatnot-else pod
- THEN the pod is NOT scheduled on node05
