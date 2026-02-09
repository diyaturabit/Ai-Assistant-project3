

from langchain_core.tools import tool
from app.auth import get_admin_token
import requests


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
    response.raise_for_status()
    return response.json()


from langchain_core.tools import tool
import httpx
from app.auth import get_admin_token

@tool
async def create_ticket(payload: dict):
    """
    Payload must contain:
    email, title, priority, description(optional)
    """
    token = await get_admin_token()

    email = payload.get("email")
    title = payload.get("title")
    priority = payload.get("priority")
    description = payload.get("description", "")

    if not email or not title:
        return "❌ email and title are required"
    if priority.capitalize() not in {"Low", "Medium", "High"}:
        return "❌ priority must be Low, Medium, or High"

    api_payload = {
        "email": email,
        "title": title,
        "priority": priority.capitalize(),
        "description": description
    }

    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "http://192.168.1.70:8000/sync_tickets/create_tickets",
            json=api_payload,
            headers=headers
        )
        response.raise_for_status()
        data = response.json()

    return (
        "✅ Ticket created successfully\n"
        f"Internal DB ID: {data.get('internal_ticket_db_id')}\n"
        f"HubSpot ID: {data.get('hubspot_ticket_id')}"
    )


# from langchain_core.tools import tool
# import requests

# @tool
# def create_ticket(email: str, title: str, description: str = "", priority: str = None):
#     """
#     Create a ticket by sending a POST request to Project 2 API.
#     """
#     if not email or not title:
#         return "❌ Error: Please provide both email and title."
#     if not priority or priority.capitalize() not in {"Low", "Medium", "High"}:
#         return "❌ Error: Please provide ticket priority as Low, Medium, or High."

#     payload = {
#         "title": title,
#         "description": description,
#         "priority": priority.capitalize(),
#         "email": email
#     }

#     print("🚀 Payload to create_ticket:", payload)

#     try:
#         response = requests.post(
#             "http://192.168.1.70:8000/sync_tickets/create_tickets",
#             json=payload,
#             timeout=30
#         )
#         response.raise_for_status()
#         data = response.json()
#         return (
#             f"✅ Ticket created successfully!\n"
#             f"Internal DB ID: {data.get('internal_ticket_db_id')}\n"
#             f"HubSpot Ticket ID: {data.get('hubspot_ticket_id')}"
#         )

#     except requests.exceptions.HTTPError as e:
#         return f"❌ HTTP error: {e.response.text}"
#     except Exception as e:
#         return f"❌ Error creating ticket: {str(e)}"
