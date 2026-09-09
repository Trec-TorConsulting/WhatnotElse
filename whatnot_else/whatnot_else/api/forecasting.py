import os
import json
import frappe

@frappe.whitelist()
def predict_optimal_starting_bid(item_title, category=None, condition=None, cogs=0.0):
    """
    Use Gemini AI to analyze market trends and suggest auction start and reserve strategies.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    cogs = float(cogs or 0.0)

    prompt = f"""
You are an expert Whatnot live stream pricing strategist and auction game theorist.
Analyze this item:
- Title: {item_title}
- Category: {category or 'General'}
- Condition: {condition or 'Good'}
- Cost of Goods Sold (COGS): ${cogs:.2f}

Provide recommendations for:
1. Recommended Dollar Start Bid ($1 start vs $5 vs 50% of value to trigger bidding frenzy)
2. Target Realized Auction Range ($min - $max)
3. Reserve Price Recommendation
4. Rationale (2 bullet points explaining bidder psychology for this category)

Format as clean JSON with keys:
"recommended_start_bid": float,
"target_min": float,
"target_max": float,
"recommended_reserve": float,
"bidding_frenzy_strategy": string,
"rationale": string
"""

    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            text = response.text.strip()
            # Clean markdown JSON block if present
            if text.startswith("```json"):
                text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            frappe.log_error(f"Gemini pricing forecast error: {str(e)}", "Whatnot AI Pricing")

    # Fallback heuristic calculation
    start_bid = 1.0 if cogs < 30.0 else max(round(cogs * 0.4, 2), 5.0)
    target_min = round(cogs * 1.5, 2) if cogs > 0 else 15.0
    target_max = round(cogs * 2.5, 2) if cogs > 0 else 35.0
    reserve = round(cogs * 1.1, 2) if cogs > 50.0 else 0.0

    return {
        "recommended_start_bid": start_bid,
        "target_min": target_min,
        "target_max": target_max,
        "recommended_reserve": reserve,
        "bidding_frenzy_strategy": "$1 Start" if start_bid == 1.0 else "Strategic Low Bid",
        "rationale": "Calculated via fallback heuristic rules based on baseline inventory COGS."
    }
