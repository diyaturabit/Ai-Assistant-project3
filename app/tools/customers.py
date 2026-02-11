from langchain_core.tools import tool
from app.auth import get_admin_token
import requests
import httpx


@tool
async def fetch_customers()->dict:
    """
    Fetch all customers from the CRM backend.
    Returns a JSON object containing a list of customers.
    """
    # user_email = get_current_user_email()  
    token = await get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            "http://192.168.1.70:8000/sync_customers/get_customers",
            headers=headers,
    )
    print(f"response for viewing customers:",response)
    response.raise_for_status()
    return response.json()

from langchain.tools import tool
import httpx

@tool
async def create_customers(email:str,payload: dict) -> str:
    """
    Create a new customer and sync to HubSpot.

    Required fields:
    - name
    - email
    - company
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
            "http://192.168.1.70:8000/sync_customers/crea_customers",
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



@tool
async def delete_customer(payload: dict) -> str:
    """
    Delete a customer using their email address.
    Required field: email.
    This removes the customer from internal DB and HubSpot.
    """

    email = payload.get("email")

    if not email:
        return "❌ Email is required to delete a customer."

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1️⃣ Get customer by email first
        get_response = await client.get(
            f"http://192.168.1.70:8000/sync_customers/get_customers",
            params={"email": email},
        )
        print(f"Get_response:",get_response)
        if get_response.status_code == 404:
            return "❌ Customer not found."

        get_response.raise_for_status()
        customer_data = get_response.json()
        customer_id = customer_data.get("customer", {}).get("id")
        print(f"Customer_id:",customer_id)
        if not customer_id:
            return "❌ Unable to find customer ID."

        # 2️⃣ Call delete endpoint
        delete_response = await client.delete(
            "http://192.168.1.70:8000/sync_customers/delete_customer",
            json={"customer_id": customer_id},
        )
        print(f"Delete_response")

        delete_response.raise_for_status()
        result = delete_response.json()

    return (
        "✅ Customer deleted successfully\n"
        f"Email: {result.get('email')}\n"
        f"HubSpot Deleted: {result.get('hubspot_deleted')}"
    )
