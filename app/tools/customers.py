from langchain_core.tools import tool
from app.auth import get_admin_token
import requests
import httpx
from config import PROJECT2_URL
@tool
async def fetch_customers()->dict:
    """
    Tool: fetch_customers
    Purpose:
    - Retrieve all customers from the internal CRM.
    - Format results in a human-readable table or JSON depending on user request.
    - Limit results to the first 15 customers. If more exist, include:
      "Showing first 15 results. There are <N> more available."
    - Do NOT return raw API output.
    - Always parse customer fields: ID, Name, Email, Company, Age.
    - Respect user-specified output formats:
      • Table → columns: ID | Name | Email | Company | Age
      • JSON → valid JSON object containing customers list
    Rules for LLM:
    - Call this tool when the user asks for:
      • "view customers", "list customers", "show customers"
    - Never call if user asks unrelated questions.
    - Return a clear summary if no customers exist: "No customers found."

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
    Tool: create_customers
    Purpose:
    - Create a new customer and optionally sync it with HubSpot.
    - Requires the following fields:
      • name (string) — customer full name
      • email (string) — customer email address
      • company (string) — company name
    - Optional:
      • age (integer)
    - Returns a confirmation message with internal customer ID and HubSpot contact ID.
    Rules for LLM:
    - Only call this tool when **all required fields are provided**.
    - If fields are missing, ask the user **one at a time** for name, email, or company.
    - Normalize priority of fields internally if needed.
    - Respect output format rules:
      • Human-readable → "✅ Customer created successfully\nCustomer ID: X\nHubSpot Contact ID: Y"
      • JSON → return structured JSON if user requests JSON output.
    - Do not simulate creation — only respond with the tool’s actual result.
    - Use this tool when user asks:
      • "add customer", "create customer", "new customer"

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
    Tool: delete_customer
    Purpose:
    - Delete a customer by `customer_id` from the internal CRM.
    - Deletes associated HubSpot contact if exists.
    - Clears cache after deletion.
    - Returns deletion confirmation, including email and HubSpot deletion status.
    Rules for LLM:
    - Only call this tool when the user **explicitly asks to delete a customer**, e.g.,
      • "delete customer 123"
      • "remove customer 456"
      • "delete customer by id 789"
    - Extract numeric `customer_id` from the user query.
    - If `customer_id` is missing, ask the user: "Please provide the customer ID."
    - Respect output format rules:
      • Human-readable → "✅ Customer deleted successfully\nEmail: X\nHubSpot Deleted: Y"
      • JSON → structured JSON with deletion info if user requests JSON output.
    - Never assume deletion — always rely on the tool output.
    - Do NOT simulate results or generate your own confirmation messages.

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

