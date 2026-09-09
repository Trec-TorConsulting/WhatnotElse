## 1. Payout Batch Data Model

- [x] 1.1 Create `Whatnot Payout Batch` DocType (JSON schema and Python controller)
- [x] 1.2 Create `Whatnot Payout Order Link` child DocType for mapping orders to batches

## 2. Payout Reconciliation & Tax Engine

- [x] 2.1 Implement Stripe payout CSV parser in `whatnot_else/api/payouts.py`
- [x] 2.2 Implement 1099-K tax summary calculator in `whatnot_else/api/payouts.py`

## 3. Financial Reports

- [x] 3.1 Implement `Whatnot Show Profitability` Script Report (`.json`, `.py`, `.js`)
- [x] 3.2 Implement `Whatnot Item Margin Analysis` Script Report (`.json`, `.py`, `.js`)

## 4. Verification and Git Lifecycle Operations

- [x] 4.1 Validate Python syntax and JSON schema files
- [ ] 4.2 Commit with Conventional Commits, push branch, create PR, and merge with admin override
