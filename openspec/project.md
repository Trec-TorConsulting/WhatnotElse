# WhatnotElse — Master OpenSpec Project Document

> **Spec Schema**: spec-driven | **Version**: 1.0.0 | **Date**: 2026-09-09
> **Author**: Tobey Rector | **AI Tools**: Antigravity + Gemini CLI
> **Status**: APPROVED FOR BUILD

---

## 1. Project Overview

**whatnot_else** is a full-enterprise, production-ready Frappe/ERPNext v16 custom application purpose-built for **Whatnot sellers**. It provides an end-to-end business operations platform covering inventory management, live show planning, order fulfillment, financials, multi-platform cross-listing, and AI-powered selling intelligence.

### What is Whatnot?
Whatnot is a live shopping marketplace where sellers host real-time video streams to sell items through auctions and "Buy It Now" listings. It is a dominant platform for trading cards, collectibles, coins, vintage fashion, sneakers, and other enthusiast categories. Sellers manage inventory, schedule shows, fulfill orders via USPS, and receive payouts via Stripe (~11% platform fee).

### Why ERPNext/Frappe?
ERPNext provides battle-tested DocType-driven data modeling, a robust permissions engine, built-in REST API, scheduled tasks (hooks), workflow automation, and a mobile-responsive desk — all open source and self-hostable on the existing K3S cluster.

### Guiding Principles
1. **Enterprise Grade** — built for scale, audited, role-gated, reliable
2. **Production Ready** — tested, documented, deployable via existing cluster tooling
3. **User Friendly** — mobile-first, dark mode, intuitive navigation for sellers who are NOT engineers
4. **Whatnot Native** — deep feature parity with Whatnot Seller Hub, then exceeds it

---

## 2. Repository Structure

```
WhatnotElse/                      ← App source repo (this repo)
├── openspec/
│   ├── config.yaml               ← OpenSpec AI context
│   ├── project.md                ← THIS FILE — master spec
│   ├── changes/                  ← Approved change proposals
│   └── specs/
│       ├── inventory/spec.md
│       ├── live-shows/spec.md
│       ├── orders/spec.md
│       ├── fulfillment/spec.md
│       ├── financials/spec.md
│       ├── crm/spec.md
│       ├── purchasing/spec.md
│       ├── multi-platform/spec.md
│       ├── ai-features/spec.md
│       ├── analytics/spec.md
│       ├── infra/spec.md
│       └── security/spec.md
├── whatnot_else/                 ← Frappe app Python module
│   ├── __init__.py
│   ├── hooks.py
│   ├── patches.txt
│   ├── modules.txt
│   ├── whatnot_else/             ← Module (maps to ERPNext module)
│   │   ├── doctype/
│   │   ├── page/
│   │   ├── report/
│   │   └── dashboard/
│   └── api/                      ← Custom REST endpoints & webhook receivers
├── setup.py
├── MANIFEST.in
└── README.md

HomeLab-Redo/whatnot-else/        ← K3S manifests (separate cluster repo)
├── namespace.yaml
├── configmap.yaml
├── pvc-sites.yaml
├── mariadb-statefulset.yaml
├── mariadb-backup-cronjob.yaml
├── redis-cache.yaml
├── redis-queue.yaml
├── redis-socketio.yaml
├── frappe-python.yaml
├── frappe-workers.yaml
├── frappe-scheduler.yaml
├── frappe-socketio.yaml
├── nginx-static-configmap.yaml
├── nginx-static-service.yaml
├── httproute.yaml
├── certificate.yaml
├── referencegrant.yaml
├── gateway-middlewares.yaml
├── secret.yaml                   ← Template only; real secret applied locally
├── site-init-job.yaml
├── pdb.yaml
└── README.md
```

---

## 3. Technology Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| **Framework** | Frappe v16 / ERPNext v16 | `frappe/erpnext:version-16` |
| **Backend Language** | Python 3.11+ | Frappe standard |
| **Frontend** | Frappe Desk + Custom Web Pages | Mobile-first, dark theme |
| **Database** | MariaDB 10.6+ | StatefulSet on K3S |
| **Cache / Queue** | Redis (3× — cache, queue, socketio) | Existing pattern from frappe ns |
| **Container Runtime** | K3S (containerd) | |
| **Registry** | registry.maddscientist.com | Private |
| **Orchestration** | K3S — Namespace: `whatnot-else` | Fully isolated |
| **Storage** | Longhorn (default StorageClass) | RWX for sites, RWO for MariaDB |
| **Ingress** | Traefik Gateway API — HTTPRoute | Parent: `kube-system/cluster-gateway` |
| **TLS** | cert-manager + Let's Encrypt | DNS-01 (Cloudflare) or HTTP-01 |
| **External AI** | Gemini API (Google AI) | Listing copy, pricing, forecasting |
| **Local AI** | Ollama on node05 (GPU) | Private/sensitive inference |
| **Payments** | Stripe | Payout reconciliation |
| **Shipping** | USPS API + Whatnot label gen | Bulk Zebra/DYMO printing |
| **Monitoring** | Uptime Kuma (node00) | External availability monitor |

---

## 4. Infrastructure Specification

### 4.1 Namespace

```yaml
# whatnot-else/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: whatnot-else
  labels:
    app.kubernetes.io/managed-by: kubectl
    environment: production
```

### 4.2 Network & Routing

- **Public hostname**: `whatnotelse.com`, `www.whatnotelse.com`
- **Internal Frappe site**: `client.whatnotelse.com`
- **Gateway**: `kube-system/cluster-gateway` — VIP `192.168.4.7`
- **HTTPRoute**: `whatnot-else` namespace → Gateway API (no legacy Ingress)
- **TLS**: cert-manager Certificate — DNS-01 or HTTP-01 issuer

### 4.3 Node Scheduling

All pods **MUST** exclude node05 (GPU-only, tainted `gpu-only:NoSchedule`):

```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: NotIn
          values: ["node05"]
```

> Schedule on node01–node04 (RPi 5, ARM64) or node06–node09 (Intel x86_64)

### 4.4 Storage

| PVC | Class | Access | Size | Purpose |
|-----|-------|--------|------|---------|
| `whatnot-sites` | longhorn | RWX | 20Gi | Frappe sites volume |
| `whatnot-mariadb` | longhorn | RWO | 50Gi | MariaDB data |

### 4.5 AI Connectivity

- **Gemini API**: External HTTPS — API key in Kubernetes Secret
- **Ollama**: `http://ollama.ollama.svc.cluster.local:11434` — in-cluster, node05 GPU

---

## 5. Frappe App Architecture

### 5.1 App Bootstrap

```bash
# On Frappe bench
bench new-app whatnot_else
bench --site client.whatnotelse.com install-app whatnot_else
```

### 5.2 Module Definition (`modules.txt`)

```
Whatnot Else
```

### 5.3 Core DocTypes

#### 5.3.1 Whatnot Seller Profile
Links an ERPNext user to one or more Whatnot seller accounts.

| Field | Type | Notes |
|-------|------|-------|
| seller_name | Data | Display name |
| whatnot_username | Data | @handle |
| seller_id | Data | Whatnot internal seller ID |
| oauth_token | Password | Encrypted; used for API (Phase 2) |
| api_token | Password | Webhook/integration auth |
| categories | Table | WN Seller Category rows |
| active | Check | Enable/disable |
| linked_user | Link → User | ERPNext user |

#### 5.3.2 Whatnot Item
Extends ERPNext Item with Whatnot-specific fields.

| Field | Type | Notes |
|-------|------|-------|
| item_code | Link → Item | ERPNext item |
| whatnot_listing_id | Data | Whatnot listing ID |
| category | Select | Trading Cards, Collectibles, Coins, etc. |
| subcategory | Data | |
| condition | Select | Mint, Near Mint, Excellent, Good, Poor |
| grade | Data | PSA/BGS grade if applicable |
| grading_company | Select | PSA, BGS, SGC, Raw |
| set_name | Data | Card set / collection |
| year | Int | Release year |
| sku | Data | Internal SKU |
| cogs | Currency | Cost of Goods Sold |
| purchase_source | Select | Flea Market, Estate Sale, Distributor, Wholesale, Other |
| whatnot_price | Currency | Listed price on Whatnot |
| floor_price | Currency | Min acceptable auction price |
| bin_price | Currency | Buy It Now price |
| platform_fee_pct | Percent | Default 11% |
| barcode | Barcode | UPC/EAN/internal |
| qr_code | Attach | QR for mobile lookup |
| status | Select | Draft, Listed, Live, Sold, Relisted, Archived |
| show_history | Table | Linked show appearances |

#### 5.3.3 Whatnot Show
Represents a planned or past Whatnot live stream.

| Field | Type | Notes |
|-------|------|-------|
| show_name | Data | Title |
| seller_profile | Link → Whatnot Seller Profile | |
| whatnot_show_id | Data | Whatnot livestream ID (Phase 2) |
| scheduled_date | Datetime | |
| end_date | Datetime | |
| status | Select | Planned, Live, Completed, Cancelled |
| stream_url | Data | Whatnot show URL |
| show_items | Table | Whatnot Show Item rows |
| total_sales | Currency | Auto-calculated |
| total_profit | Currency | Auto-calculated |
| platform_fees | Currency | |
| notes | Text Editor | |
| show_type | Select | Auction, BIN, Mixed, Break |

#### 5.3.4 Whatnot Show Item
Child table for items in a show.

| Field | Type | Notes |
|-------|------|-------|
| whatnot_item | Link → Whatnot Item | |
| sequence | Int | Order in show |
| start_price | Currency | Auction start |
| sold_price | Currency | Final price |
| sold | Check | |
| buyer | Link → Customer | |
| order_id | Data | Whatnot order ID |

#### 5.3.5 Whatnot Order
Imported from Whatnot CSV or webhook. Maps to ERPNext Sales Order.

| Field | Type | Notes |
|-------|------|-------|
| whatnot_order_id | Data | Unique Whatnot order ID |
| seller_profile | Link → Whatnot Seller Profile | |
| buyer_name | Data | |
| buyer_whatnot_username | Data | |
| customer | Link → Customer | ERPNext customer |
| order_date | Datetime | |
| items | Table | Whatnot Order Item rows |
| subtotal | Currency | |
| platform_fee | Currency | |
| shipping_charged | Currency | |
| net_payout | Currency | |
| status | Select | Pending, Processing, Shipped, Delivered, Cancelled, Refunded |
| sales_order | Link → Sales Order | ERPNext SO |
| show | Link → Whatnot Show | If from a show |
| shipping_label_url | Data | |
| tracking_number | Data | |
| usps_label_printed | Check | |
| packing_slip_printed | Check | |
| source | Select | Show Auction, BIN, Storefront, CSV Import |

#### 5.3.6 Platform Integration
Stores credentials and sync state for external platforms.

| Field | Type | Notes |
|-------|------|-------|
| platform | Select | eBay, Shopify, WooCommerce, Mercari |
| seller_profile | Link → Whatnot Seller Profile | |
| api_key | Password | |
| api_secret | Password | |
| access_token | Password | |
| store_url | Data | |
| sync_enabled | Check | |
| last_sync | Datetime | |
| sync_log | Table | Sync Log Entry rows |

#### 5.3.7 AI Prompt Template
User-editable prompt templates for AI features.

| Field | Type | Notes |
|-------|------|-------|
| template_name | Data | |
| feature | Select | Listing Copy, Price Suggest, Demand Forecast, Custom |
| provider | Select | Gemini, Ollama |
| model | Data | gemini-1.5-pro, llama3, etc. |
| system_prompt | Text Editor | |
| user_prompt_template | Text Editor | Use {{item_name}}, {{category}}, etc. |
| active | Check | |

---

## 6. Module Specifications

### Module 1 — Inventory Management

**Goal**: Complete lifecycle management of all items a seller owns, from acquisition to sale.

**Key Capabilities**:
- Bulk CSV import of Whatnot inventory exports
- Item entry with full attributes (category, condition, grade, COGS, pricing)
- Barcode/QR generation and mobile scanning → instant item lookup
- SKU management with internal tracking fields (hidden from buyers)
- Multi-condition item variants (graded vs. raw)
- Inventory valuation (COGS, unrealized profit)
- Reorder alerts and low-stock warnings
- Category-specific attribute schemas (trading card grade, coin grade, shoe size)

**DocTypes**: Whatnot Item, Whatnot Item Category Schema
**Frappe Hooks**: `on_submit` on Sales Order → mark item Sold; `scheduled_tasks` for reorder check
**ERPNext Integration**: Links to ERPNext `Item`, `Warehouse`, `Stock Entry`

---

### Module 2 — Live Show Planner

**Goal**: Plan, run, and analyze Whatnot live shows from a calendar-driven workspace.

**Key Capabilities**:
- Calendar view of scheduled and past shows (Frappe Calendar or custom page)
- Show creation: title, date/time, show type (Auction/BIN/Break), item assignment
- Drag-and-drop item sequencing for a show
- Real-time show status tracking (Planned → Live → Completed)
- Post-show analytics: total sold, revenue, profit, unsold items
- Giveaway item flagging
- Break management (multi-spot breaks for card categories)
- Stream URL auto-fill when show goes live (Phase 2: Whatnot webhook)

**DocTypes**: Whatnot Show, Whatnot Show Item, Whatnot Break Slot
**Custom Page**: `show-planner` — Frappe Web Page with calendar + item list drag UI

---

### Module 3 — Order Management

**Goal**: Full order lifecycle from Whatnot sale to fulfillment and closure.

**Phase 1 (CSV Import)**:
- Import Whatnot order CSV export → create Whatnot Order docs
- Auto-create ERPNext Customer for new buyers
- Auto-create ERPNext Sales Order from Whatnot Order
- Duplicate detection by `whatnot_order_id`

**Phase 2 (API/Webhooks)**:
- Webhook receiver at `/api/method/whatnot_else.api.webhooks.handle`
- Verify Whatnot webhook signature (HMAC)
- Real-time `Order Created` / `Order Updated` events

**Order Lifecycle**:
```
Pending → Processing → Packed → Label Printed → Shipped → Delivered
                                              ↘ Cancelled / Refunded
```

**DocTypes**: Whatnot Order, Whatnot Order Item
**ERPNext Links**: Customer, Sales Order, Delivery Note, Payment Entry

---

### Module 4 — Fulfillment & Shipping

**Goal**: Streamlined packing and shipping workflow optimized for high-volume show days.

**Key Capabilities**:
- Batch packing queue (group orders by show or date)
- USPS label generation (via Whatnot API Phase 2 or direct USPS/EasyPost API)
- Bulk label printing — Zebra ZPL or DYMO (via browser print API or Frappe Print Format)
- Packing slip PDF generation (Frappe Print Format)
- Tracking number entry and auto-update
- Delivery confirmation tracking
- Scan-to-pack workflow (scan order barcode → mark packed)

**DocTypes**: Whatnot Shipment Batch, Whatnot Shipment Batch Item
**Print Formats**: Whatnot Packing Slip, Whatnot Shipping Label (ZPL template)
**Custom Page**: `packing-station` — mobile-friendly scan-to-pack interface

---

### Module 5 — Financial / P&L

**Goal**: Accurate, real-time profit/loss tracking per item, per show, per time period.

**Key Calculations**:
- **Gross Revenue** = sold_price
- **Platform Fee** = sold_price × 0.11 (configurable per seller)
- **Shipping Cost** = actual cost (USPS label cost)
- **COGS** = item.cogs
- **Net Profit** = Gross Revenue − Platform Fee − Shipping Cost − COGS

**Key Capabilities**:
- P&L per show (automatic after show completes)
- P&L per item (lifetime profitability)
- Stripe payout reconciliation (import Stripe payout CSVs)
- Platform fee ledger
- 1099-K tax reporting (annual payout summary by seller)
- Seller payout tracking by period

**DocTypes**: Whatnot Payout, Whatnot Payout Item, Whatnot Tax Summary
**Reports**: Show P&L, Inventory Valuation, Annual Tax Summary (1099), Seller Payout Register
**ERPNext Links**: Journal Entry, Payment Entry, Account (chart of accounts integration)

---

### Module 6 — Customer / Buyer CRM

**Goal**: Build a seller's knowledge of their best buyers and repeat customers.

**Key Capabilities**:
- Auto-create ERPNext Customer on first order
- Buyer profile: Whatnot username, total spent, order count, categories purchased
- VIP buyer flag (auto-promote on spend threshold)
- Seller notes per buyer (private)
- Purchase history timeline
- "Frequent buyer" report (top N buyers by spend/volume)
- Buyer block list (flag problematic buyers)

**DocTypes**: Extends ERPNext `Customer` with custom fields
**Custom Fields**: whatnot_username, vip_buyer, buyer_notes, block_listed, total_whatnot_spend
**Reports**: Top Buyers by Revenue, Repeat Buyer Frequency, New vs. Returning Buyers

---

### Module 7 — Purchasing / Restocking

**Goal**: Track inventory acquisition from all sources — distributors, flea markets, estate sales.

**Key Capabilities**:
- Purchase Order creation linked to vendors
- Vendor management (distributor, flea market, auction house, estate sale)
- Receiving workflow (PO → receive → add to inventory)
- COGS auto-populate from purchase cost
- Reorder point alerts (email/notification when stock < threshold)
- Personal shopper mode: log flea market / estate sale finds as a "Sourcing Run"
- Sourcing Run P&L (total spent per run vs. total sold from run)

**DocTypes**: Whatnot Sourcing Run, Whatnot Sourcing Item
**ERPNext Links**: Purchase Order, Supplier, Stock Entry (material receipt)

---

### Module 8 — Multi-Platform Sync

**Goal**: Prevent overselling by maintaining synchronized inventory across platforms.

**Supported Platforms (Phase 1)**: Manual export/import
**Supported Platforms (Phase 2)**: eBay API, Shopify API, Mercari (if API available)

**Key Capabilities**:
- Cross-listing status per item (Whatnot, eBay, Shopify, Mercari)
- Inventory lock when item goes live on Whatnot (prevent eBay/Shopify sale)
- Sync log with success/failure tracking
- Platform credentials vault (Kubernetes Secret-backed)
- Conflict resolution: Whatnot wins (sold live = remove everywhere)

**DocTypes**: Platform Integration, Platform Listing, Platform Sync Log
**Frappe Hooks**: `after_save` on Whatnot Item → trigger sync queue

---

### Module 9 — AI-Powered Features

**Goal**: Reduce seller manual work and improve sales outcomes via AI intelligence.

#### 9.1 Listing Copy Generator (Gemini API)
- Input: item name, category, condition, grade, set
- Output: SEO-optimized Whatnot listing title + description
- Model: `gemini-1.5-pro` or `gemini-2.0-flash`
- Tone: engaging, community-appropriate

#### 9.2 Price Suggestion Engine (Gemini + historical data)
- Input: item details + recent sold comps from internal history
- Output: suggested starting bid, BIN price, floor price
- Considers: category trends, condition premium, platform fee

#### 9.3 Demand Forecasting (Ollama — private)
- Input: item category, historical sell-through rate, show schedule
- Output: likelihood of sale in next N shows, recommended show placement
- Model: Ollama local (llama3 or mistral on node05 GPU)
- Private: uses internal sales data only — stays on cluster

#### 9.4 Show Planning Assistant (Gemini)
- Input: available inventory + past show performance
- Output: recommended item order for next show (maximize engagement + revenue)

**DocTypes**: AI Prompt Template, AI Generation Log
**API**: `whatnot_else.api.ai.generate_listing_copy`, `whatnot_else.api.ai.suggest_price`
**Security**: Gemini API key in Kubernetes Secret, never logged

---

### Module 10 — Reporting & Analytics

**Goal**: Give sellers the data they need to make smarter business decisions.

**Dashboards**:
1. **Seller Dashboard** — today's sales, active shows, pending orders, recent profit
2. **Show Performance Dashboard** — per-show: revenue, sell-through %, avg price, profit
3. **Inventory Health Dashboard** — total items, total COGS, unrealized value, stale items
4. **Platform Comparison Dashboard** — Whatnot vs. eBay vs. Shopify revenue side-by-side

**Reports**:
| Report | Type | Notes |
|--------|------|-------|
| Show P&L | Script | Per show: revenue, fees, COGS, profit |
| Item Profitability | Script | Lifetime profit per item |
| Inventory Valuation | Script | Total COGS, FMV, unrealized gain |
| Top Buyers | Script | By revenue and order count |
| Platform Revenue Comparison | Script | Cross-platform revenue |
| Annual Tax Summary (1099) | Script | Stripe payout total per year |
| Sourcing ROI | Script | Per sourcing run profitability |
| Category Sell-Through | Script | % sold per category over period |

**Charts**: Use Frappe Charts (built-in) + custom dashboard pages for advanced visualizations

---

## 7. Whatnot API Integration Roadmap

### Phase 1 — CSV Import (NOW)
- Whatnot Seller Hub exports: Orders CSV, Payout Ledger CSV, Inventory CSV
- Frappe Data Import tool + custom import controller
- Endpoint: `whatnot_else.controllers.csv_import`

### Phase 2 — GraphQL API (When API Access Granted)
- Auth: OAuth 2.0 with Bearer token
- Endpoints:
  - `https://api.whatnot.com/seller-api/graphql` (production)
  - `https://api.stage.whatnot.com/seller-api/graphql` (staging)
- Scopes: `read:inventory`, `write:inventory`, `read:customers`
- Operations: Query listings, create/update listings, fetch orders

### Phase 2 — Webhook Receiver
```
POST /api/method/whatnot_else.api.webhooks.handle
Authorization: Bearer {whatnot_webhook_secret}
```
Supported events:
- `listing.created`, `listing.updated`
- `order.created`, `order.updated`, `shipment.label_created`
- `livestream.created`, `livestream.stopped`, `livestream.product_added`, `livestream.product_removed`

---

## 8. Security Model

### 8.1 Roles

| Role | Access |
|------|--------|
| **Admin** | Full access — all DocTypes, settings, integrations |
| **Seller** | Own profile's items, shows, orders; no financial admin |
| **Warehouse Staff** | Inventory, fulfillment, packing; read orders; no financials |
| **Accountant** | Financial reports, payouts, tax; read-only on items/orders |

### 8.2 Multi-Seller
- Each `Whatnot Seller Profile` is isolated by user permission
- Sellers only see their own items, shows, orders, and reports
- Admin sees all

### 8.3 API Token Auth
- Webhook endpoints validate `Authorization: Bearer {token}` against hashed `Whatnot Seller Profile.api_token`
- Integration endpoints use ERPNext API token authentication

### 8.4 Audit Log
- All DocType mutations captured via Frappe's built-in `Track Changes` + `Version`
- Critical actions (price changes, order status, payout records) logged to `Whatnot Audit Log` DocType

### 8.5 Secrets Management
- All API keys (Gemini, eBay, Shopify, Stripe, USPS) stored in Kubernetes Secrets
- Frappe reads from environment variables injected by K3S Deployment
- Never committed to git; `secret.yaml` is a template with placeholder values only

---

## 9. UX & Design Requirements

### 9.1 Design Principles
- **Mobile-first** — sellers pack orders on phones; core workflows must be usable on 6" screen
- **Dark mode** — custom Frappe theme with dark palette (seller studio environment)
- **Speed** — no page should take >2s to load; dashboards lazy-load charts
- **Intuitive** — zero training required for core workflows (order packing, item entry)

### 9.2 Custom Pages & Interfaces
| Page | Path | Purpose |
|------|------|---------|
| Seller Dashboard | `/seller-dashboard` | Main hub: KPIs, active show, pending orders |
| Show Planner | `/show-planner` | Calendar + drag-drop item sequencing |
| Packing Station | `/packing-station` | Scan-to-pack mobile workflow |
| Item Scanner | `/scan` | Barcode/QR → item card (mobile) |
| Analytics Hub | `/analytics` | All charts and reports in one place |

### 9.3 Notification System
- **Email**: order alerts, restock alerts, daily summary
- **In-Frappe notifications**: real-time desk notifications for order events
- **SMS** (optional Phase 2): Twilio integration for urgent alerts

### 9.4 Print Formats
- **Packing Slip** (PDF): order details, items, buyer address, thank-you message
- **Shipping Label** (ZPL/PDF): Zebra-compatible label format
- **Bulk Print Queue**: select multiple orders → print all labels in one batch

---

## 10. K3S Deployment Architecture

### Manifest File Map (HomeLab-Redo/whatnot-else/)

All manifests mirror the existing `frappe/` namespace pattern.

| Manifest | Notes |
|----------|-------|
| `namespace.yaml` | `whatnot-else` namespace |
| `configmap.yaml` | `common_site_config.json` — MariaDB host, Redis hosts, site name |
| `pvc-sites.yaml` | Longhorn RWX 20Gi — sites volume |
| `mariadb-statefulset.yaml` | MariaDB StatefulSet + Service; Longhorn RWO 50Gi |
| `mariadb-backup-cronjob.yaml` | Daily MariaDB backup to Longhorn |
| `redis-cache.yaml` | Redis cache instance |
| `redis-queue.yaml` | Redis queue instance |
| `redis-socketio.yaml` | Redis socketio instance |
| `frappe-python.yaml` | gunicorn web service (2 replicas) + Service |
| `frappe-workers.yaml` | Background workers (short, long, default queues) |
| `frappe-scheduler.yaml` | Singleton scheduler Deployment |
| `frappe-socketio.yaml` | Socket.io realtime service |
| `nginx-static-configmap.yaml` | nginx static assets config |
| `nginx-static-service.yaml` | Static asset Service |
| `httproute.yaml` | Gateway HTTPRoute — whatnotelse.com + www.whatnotelse.com |
| `certificate.yaml` | cert-manager Certificate (HTTP-01 or DNS-01) |
| `referencegrant.yaml` | Allow kube-system gateway to route to whatnot-else ns |
| `gateway-middlewares.yaml` | gzip, security headers, Frappe site header |
| `secret.yaml` | Template — all API keys, DB password, Frappe admin password |
| `site-init-job.yaml` | One-time: `bench new-site`, install ERPNext + whatnot_else |
| `pdb.yaml` | PodDisruptionBudget for HA |

### Container Image Strategy
- **Base image**: `frappe/erpnext:version-16`
- **Custom image**: `registry.maddscientist.com/whatnot-else/erpnext-whatnot:latest`
- Build: `docker buildx build --platform linux/arm64,linux/amd64` (multi-arch for RPi + Intel nodes)
- Install `whatnot_else` app during image build via `bench get-app` or local copy

---

## 11. Development Phases

### Phase 1 — Foundation (Build Now)
- [ ] Frappe app scaffold (`bench new-app whatnot_else`)
- [ ] K3S namespace + all manifests (HomeLab-Redo/whatnot-else/)
- [ ] Core DocTypes: Seller Profile, Whatnot Item, Whatnot Show, Whatnot Order
- [ ] CSV import controllers (orders, inventory, payouts)
- [ ] Role + permission setup (Admin, Seller, Warehouse Staff, Accountant)
- [ ] Basic Show Planner (list view + item assignment)
- [ ] Order Management (list, detail, status workflow)
- [ ] Fulfillment (packing slip PDF, label print)
- [ ] Financial P&L (per-show report, per-item report)
- [ ] Seller Dashboard (custom Frappe page)
- [ ] Dark mode theme
- [ ] Barcode/QR item lookup page (mobile)

### Phase 2 — Integrations
- [ ] Whatnot GraphQL API client (when access granted)
- [ ] Webhook receiver (authenticated, HMAC verified)
- [ ] eBay API cross-listing
- [ ] Shopify sync
- [ ] AI features (Gemini + Ollama)
- [ ] Advanced analytics dashboards
- [ ] SMS notifications (Twilio)
- [ ] Stripe payout reconciliation (CSV + API)

### Phase 3 — Scale & Polish
- [ ] Multi-tenant (multiple sellers on one instance)
- [ ] USPS/EasyPost direct API integration
- [ ] Mobile PWA wrapper
- [ ] 1099-K tax reporting automation
- [ ] Advanced AI: demand forecasting, show optimization

---

## 12. Open Questions / Decisions Pending

| # | Question | Priority | Decision |
|---|----------|----------|---------|
| 1 | Register `whatnotelse.com` — done or needed? | HIGH | TBD — confirm DNS in Cloudflare |
| 2 | Custom ERPNext image built in cluster registry or external CI? | HIGH | TBD |
| 3 | USPS label API: direct USPS eVS or EasyPost/ShipStation? | MEDIUM | TBD |
| 4 | Whatnot API access application — submitted? | MEDIUM | Email sellerapi@whatnot.com |
| 5 | Stripe payout CSV format for reconciliation | MEDIUM | Get sample CSV |
| 6 | Zebra/DYMO — which model printers in use? | LOW | TBD |
| 7 | eBay Store URL / seller ID for integration | LOW | TBD |
| 8 | Gemini API key — AI Studio or Vertex AI project? | HIGH | TBD |

---

## 13. Glossary

| Term | Definition |
|------|-----------|
| **Whatnot** | Live shopping marketplace; sellers stream video to sell via auction/BIN |
| **Show** | A single Whatnot live stream session |
| **BIN** | Buy It Now — fixed-price listing |
| **Break** | Multi-buyer group purchase of a sealed product (e.g. a case of card packs) |
| **COGS** | Cost of Goods Sold — what the seller paid for the item |
| **Platform Fee** | Whatnot's ~11% fee on gross sale price |
| **Net Payout** | Revenue after platform fee and shipping |
| **1099-K** | US tax form for payment processors; issued when annual payouts exceed threshold |
| **Frappe** | Open-source web framework underlying ERPNext |
| **DocType** | Frappe's model abstraction — defines a form, a database table, and an API |
| **Bench** | Frappe's CLI tool for managing sites, apps, and workers |
| **K3S** | Lightweight Kubernetes distribution used in the homelab cluster |
| **HTTPRoute** | Gateway API resource (replaces Ingress) for routing traffic |
| **Longhorn** | Cloud-native distributed storage for Kubernetes |
