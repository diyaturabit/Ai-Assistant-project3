

from langchain_core.tools import tool
from app.auth import get_admin_token
import requests
import httpx


@tool
def fetch_tickets(status: str | None = None, priority: str | None = None):
    """
    Fetch tickets from CRM system.
    """
    params = {}
    if status:
        params["status"] = status
    if priority:
        params["priority"] = priority

    response = requests.get(
        "http://192.168.1.70:8000/sync_tickets/tickets_get",
        params=params,
        timeout=30,
    )
    print(f"response for viewing tickets:",response)
    response.raise_for_status()
    return response.json()

@tool
async def create_ticket(payload: dict):
    """
    Payload must contain:
    email, title, priority, description(optional)
    """
    token = await get_admin_token()
    print(f"Create ticket token:",token)
    email = payload.get("email")
    title = payload.get("title")
    priority = payload.get("priority")
    description = payload.get("description", "")

    if not email or not title:
        return "❌ email and title are required"
    if priority.capitalize() not in {"Low", "Medium", "High"}:
        return "❌ priority must be Low, Medium, or High"

    api_payload = {
        "payload":
        {
        "email": email,
        "title": title,
        "priority": priority.capitalize(),
        "description": description
        }
    }
    print(f"API PAYLOAD:",api_payload)
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "http://192.168.1.70:8000/sync_tickets/create_tickets",
            json=api_payload,
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        print(f"Create ticket data:",data)
    return (
        "✅ Ticket created successfully\n"
        f"Internal DB ID: {data.get('internal_ticket_db_id')}\n"
        f"HubSpot ID: {data.get('hubspot_ticket_id')}"
    )

