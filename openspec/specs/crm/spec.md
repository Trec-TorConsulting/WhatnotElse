# Spec: Customer / Buyer CRM

## Capability
Build seller knowledge of their best buyers, track repeat customers,
and flag VIP and problematic buyers.

## Requirements

### Requirement: Auto-create ERPNext Customer on first order
- When a Whatnot Order is imported/created for a new buyer
- ERPNext Customer is created with: name = buyer_name, whatnot_username = handle
- Subsequent orders link to same Customer by whatnot_username match

### Requirement: Buyer profile enrichment
- Seller can add private notes per buyer
- VIP flag: manually set, or auto-promoted when cumulative spend > threshold (configurable)
- Block flag: mark problematic buyers (non-paying, fraud)
- Purchase history timeline on Customer form

### Requirement: Buyer reports
- Top Buyers by Revenue (select period)
- Repeat Buyer Frequency (N orders in period)
- New vs. Returning Buyers (cohort view)

## Scenarios

### Scenario: VIP buyer auto-promoted
- GIVEN VIP threshold = $500 lifetime spend
- WHEN buyer's 10th order is saved, bringing total spend to $520
- THEN buyer's vip_buyer field is set to True automatically
- AND seller receives notification: "Buyer @pokefan99 has reached VIP status!"
