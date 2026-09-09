## ADDED Requirements

### Requirement: Traefik Gateway API Wildcard Subdomain Routing
The infrastructure manifests SHALL declare a Traefik Gateway API `HTTPRoute` attached to `kube-system/cluster-gateway` on VIP `192.168.4.7` matching both root domain `whatnotelse.com` and wildcard `*.whatnotelse.com`.

#### Scenario: Route request to seller subdomain
- **WHEN** an incoming HTTPS request targets `https://seller1.whatnotelse.com`
- **THEN** Traefik routes the request to the Frappe web service within the `whatnot-else` namespace without manual ingress reconfiguration.

### Requirement: Node05 GPU Affinity Exclusion
All application workloads, background workers, and database pods SHALL declare node anti-affinity or node exclusion rules to prevent scheduling onto `node05` (the dedicated GPU node).

#### Scenario: Pod scheduling check
- **WHEN** the Kubernetes scheduler assigns pods in the `whatnot-else` namespace
- **THEN** pods are scheduled exclusively onto ARM64 or general x86 nodes, leaving `node05` reserved for GPU workloads.
