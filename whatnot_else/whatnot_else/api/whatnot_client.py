import json
import frappe
import requests

WHATNOT_GRAPHQL_ENDPOINT = "https://seller.whatnot.com/api/graphql"

class WhatnotGraphQLClient:
    """
    Client for interacting with Whatnot's Developer GraphQL API.
    Handles authentication, query execution, mutations, and error handling.
    """
    def __init__(self, seller_profile):
        self.seller_profile = seller_profile
        self.profile_doc = frappe.get_doc("Whatnot Seller Profile", seller_profile)
        self.api_token = self.profile_doc.get_password("api_token")

    def execute_query(self, query, variables=None):
        if not self.api_token:
            return {
                "error": True,
                "message": "API Bearer Token is not configured for this seller profile."
            }

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "User-Agent": "WhatnotElse-ERP/1.0"
        }

        payload = {
            "query": query,
            "variables": variables or {}
        }

        try:
            response = requests.post(WHATNOT_GRAPHQL_ENDPOINT, json=payload, headers=headers, timeout=15)
            if response.status_code == 200:
                return response.json()
            else:
                frappe.log_error(f"Whatnot GraphQL Error {response.status_code}: {response.text}", "Whatnot API Client")
                return {
                    "error": True,
                    "status_code": response.status_code,
                    "message": response.text
                }
        except Exception as e:
            frappe.log_error(f"Whatnot GraphQL Request Exception: {str(e)}", "Whatnot API Client")
            return {
                "error": True,
                "message": str(e)
            }

    def get_live_shows(self):
        query = """
        query GetLivestreams {
            viewer {
                livestreams(first: 20) {
                    edges {
                        node {
                            id
                            title
                            status
                            scheduledStartTime
                        }
                    }
                }
            }
        }
        """
        return self.execute_query(query)

    def update_listing_price(self, listing_id, price):
        mutation = """
        mutation UpdateListingPrice($id: ID!, $price: Float!) {
            updateListing(input: { id: $id, price: $price }) {
                listing {
                    id
                    price
                }
            }
        }
        """
        return self.execute_query(mutation, {"id": listing_id, "price": float(price)})
