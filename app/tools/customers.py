from langchain_core.tools import tool
from app.auth import get_admin_token
import requests
import httpx
from config import PROJECT2_URL
@tool
async def fetch_customers()->dict:
    """
    Fetch all customers from the CRM backend.
    Returns a JSON object containing a list of customers.
    """
    # user_email = get_current_user_email()  
    token = await get_admin_token()
    print("Fetching customers")
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            f"{PROJECT2_URL}/sync_customers/get_customers",
            headers=headers,
    )
    print(f"response for viewing customers:",response)
    response.raise_for_status()
    return response.json()

from langchain.tools import tool
import httpx

@tool
async def create_customers(payload: dict) -> str:
    """
    Create a new customer and sync to HubSpot.

    Required fields:
    - name
    - email
    - companyset_customer_mapping
    Optional:
    - age

    Returns confirmation message with internal and HubSpot IDs.
    """
    
    token = await get_admin_token()

    name = payload.get("name")
    email = payload.get("email")
    company = payload.get("company")
    age = payload.get("age")

    if not email or not name or not company:
        return "❌ name, email, and company are required."

    api_payload = {
        "name": name,
        "email": email,
        "company": company,
        "age": age
    }

    headers = {
        "Authorization": f"Bearer {token}"
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{PROJECT2_URL}/sync_customers/crea_customers",
            json=api_payload,
            headers=headers,
        )

    response.raise_for_status()
    data = response.json()

    return (
        "✅ Customer created successfully\n"
        f"Customer ID: {data.get('customer_id')}\n"
        f"HubSpot Contact ID: {data.get('hubspot_contact_id')}"
    )



@tool("delete_customer", description="Delete a customer using their customer_id")
async def delete_customer(customer_id: int):
    """
    Deletes a customer by customer_id.

    - Calls internal CRM API.
    - Deletes customer from database.
    - Deletes HubSpot contact if exists.
    - Clears Redis cache.
    - Returns deletion status.
    """

    print("Delete customer tool calling")
    token=await get_admin_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.request(
            "DELETE",
            f"{PROJECT2_URL}/sync_customers/delete_customer", 
            json={"customer_id": customer_id},
            headers=headers
        )
    # Handle not found
    if response.status_code == 404:
        return {
            "status": "Found",
            "message": f"Customer {customer_id} found."
        }
    response.raise_for_status()
    result= response.json()
    return (
        "✅ Customer deleted successfully\n"
        f"Email: {result.get('email')}\n"
        f"HubSpot Deleted: {result.get('hubspot_deleted')}"
    )

