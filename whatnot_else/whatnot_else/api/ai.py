import os
import json
import frappe
import requests

OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "http://ollama.ollama.svc.cluster.local:11434")

@frappe.whitelist()
def generate_listing_content(item_title, category=None, condition=None, key_features=None, preferred_engine="auto"):
    """
    Generate compelling Whatnot listing title, description, and hashtags
    using Google Gemini API (if GEMINI_API_KEY present) or in-cluster Ollama LLM.
    """
    prompt = f"""
You are an expert Whatnot live stream auction seller and e-commerce copywriter.
Generate an optimized Whatnot listing for:
- Product Title: {item_title}
- Category: {category or 'General'}
- Condition: {condition or 'Great'}
- Key Details: {key_features or 'N/A'}

Provide:
1. Catchy Stream Auction Headline (max 60 chars)
2. Live Show Pitch Points (3 concise bullet points to shout out on stream)
3. Full Description (2-3 paragraphs highlighting authenticity and value)
4. 5 Relevant Hashtags
"""
    gemini_key = os.getenv("GEMINI_API_KEY")

    if (preferred_engine in ("auto", "gemini")) and gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return {
                "status": "success",
                "engine": "gemini-1.5-flash",
                "content": response.text
            }
        except Exception as e:
            frappe.log_error(f"Gemini generation error: {str(e)}", "Whatnot AI Copywriter")
            if preferred_engine == "gemini":
                frappe.throw(f"Gemini API error: {str(e)}")

    # Fallback to local in-cluster Ollama
    try:
        payload = {
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
        res = requests.post(f"{OLLAMA_ENDPOINT}/api/generate", json=payload, timeout=20)
        if res.status_code == 200:
            result = res.json()
            return {
                "status": "success",
                "engine": "ollama-local",
                "content": result.get("response")
            }
    except Exception as e:
        frappe.log_error(f"Ollama generation error: {str(e)}", "Whatnot AI Copywriter")

    return {
        "status": "fallback",
        "engine": "template",
        "content": f"**{item_title}**\n\nCondition: {condition or 'Good'}\nCategory: {category or 'General'}\nAuthentic item ready for live stream auction! Bid early to lock in your deal.\n\n#Whatnot #LiveSelling #{category or 'Deals'}"
    }
