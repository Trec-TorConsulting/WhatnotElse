# Spec: AI-Powered Features

## Capability
Gemini API (external, cloud) and Ollama (in-cluster, GPU node05) power AI features
that reduce seller manual work and improve sales outcomes.

## AI Providers

| Provider | Use Cases | Privacy |
|----------|-----------|---------|
| Gemini API (gemini-1.5-pro / 2.0-flash) | Listing copy, price suggestions, show planning | External — no sensitive data |
| Ollama (node05 GPU, llama3/mistral) | Demand forecasting, private data analysis | Internal only |

## Requirements

### Requirement: Listing copy generator
- Input: item name, category, condition, grade, set, year, any notes
- Gemini generates: Whatnot listing title (max 80 chars) + description (max 500 chars)
- Tone: engaging, community-appropriate for Whatnot audience
- Seller can regenerate or edit before using
- Logged to AI Generation Log for audit

### Requirement: Price suggestion engine
- Input: item details + up to 20 recent sold comps from internal history
- Gemini returns: suggested starting bid, BIN price, floor price
- Reasoning summary shown to seller ("Similar PSA 9 Charizard sold for $240-$280...")
- Seller can accept or override

### Requirement: Demand forecasting (Ollama — private)
- Input: item category, seller's historical sell-through rate, upcoming show schedule
- Ollama (local) returns: likelihood this item sells in next show (%), recommended show slot
- Uses only internal data — never sent to external API

### Requirement: Show planning assistant (Gemini)
- Input: list of available inventory items, past 5 shows' performance data
- Gemini returns: recommended show order (sequence) with reasoning
- Output pre-populates Whatnot Show Item table for review

### Requirement: AI prompt template management
- Admin can view/edit prompt templates (system prompt + user prompt template)
- Prompt templates support variable substitution: {{item_name}}, {{category}}, etc.
- Active/inactive toggle per template

## Scenarios

### Scenario: Generate listing copy for a PSA 9 Charizard
- WHEN seller clicks "Generate Copy" on a Whatnot Item
- THEN Gemini API is called with item details
- AND within 5 seconds, title and description fields are populated
- AND seller can edit before saving

### Scenario: Price suggestion for common sports card
- WHEN seller requests price suggestion
- THEN system queries last 20 sold orders for same category/grade
- AND Gemini returns: Start: $15, BIN: $35, Floor: $12 with reasoning

### Scenario: Demand forecast uses Ollama (no external call)
- WHEN seller requests demand forecast for Trading Cards category
- THEN Frappe calls Ollama at http://ollama.ollama.svc.cluster.local:11434
- AND NO data is sent to Gemini API or any external service
- AND seller receives sell probability and recommended show slot
