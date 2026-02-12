from langchain_core.tools import tool
from app.auth import get_admin_token
import httpx
import requests


@tool
async def fetch_tickets(status: str | None = None, priority: str | None = None):
    """
    Fetch tickets from the CRM system.

    RULES:
    - Fetch only the first 15 tickets to prevent large responses.
    - Include summary:
        - Total tickets matching the query
        - Number of open tickets
        - Number of closed tickets
        - Number displayed
    - If more than 15 tickets exist, include note:
        "Showing first 15 tickets. There are <X> more tickets available."
    - Supports optional filters:
        - status: "open" or "closed"
        - priority: "Low", "Medium", "High"
    - Returns a formatted list of tickets (JSON, table, or summary depending on request).
    """
    print("Fetching ticket")
    # token = await get_admin_token()
    # headers = {"Authorization": f"Bearer {token}"}
    params = {}
    if status:
        params["status"] = status
    if priority:
        params["priority"] = priority
    # async with httpx.AsyncClient(timeout=30) as client:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(
            "http://192.168.1.70:8000/sync_tickets/tickets_get",
            params=params
        )
        print(f"Response",response)
    response.raise_for_status()
    return response.json()


@tool
async def fetch_tickets_by_email(email: str):
    """
    Fetch tickets for a specific customer email.

    RULES:
    - Fetch only the first 15 tickets to avoid large responses.
    - Include summary:
        - Total tickets matching the query
        - Number of open tickets
        - Number of closed tickets
        - Number displayed
    - If more than 15 tickets exist, include note:
        "Showing first 15 tickets. There are <X> more tickets available."
    - If no tickets are found, return:
        "No tickets found for this customer."
    - Supports optional time filters (today, this week, last week, etc.)
    """
    token = await get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            "http://192.168.1.70:8000/sync_tickets/tickets_get",
            params={"email": email},
            headers=headers
        )
    response.raise_for_status()
    tickets = response.json().get("tickets", [])
    if not tickets:
        return f"No tickets found for email {email}"
    return tickets


@tool
async def create_ticket(payload: dict):
    """
    Create a new ticket in the CRM system.

    REQUIRED FIELDS in payload:
    - email: customer email
    - title: ticket title
    - priority: Low, Medium, or High
    - description: optional

    RULES:
    - Ask for missing required fields one by one.
    - Normalize priority internally (capitalize first letter).
    - Only call tool if all required fields are present.
    - Returns a clear confirmation including:
        - Internal DB ticket ID
        - HubSpot ticket ID
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
        "payload": {
            "email": email,
            "title": title,
            "priority": priority.capitalize(),
            "description": description
        }
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


@tool
async def update_ticket_by_email(
    email: str,
    title_contains: str = None,
    new_title: str = None,
    new_description: str = None,
    new_priority: str = None,
    new_status: str = None
):
    """
    Update ticket fields for a specific customer email.

    RULES:
    - Fetch tickets for the given email.
    - Optionally filter ticket by `title_contains`.
    - Update the first matching ticket.
    - Only update fields provided (others ignored).
    - Fields that can be updated: title, description, priority, status.
    - Returns confirmation with:
        - Ticket ID
        - Updated fields
    - If no tickets match, return:
        "No tickets matched the criteria for email <email>."
    """
    token = await get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    tickets_resp = await fetch_tickets_by_email(email)
    if isinstance(tickets_resp, str):
        return tickets_resp  # no tickets found

    if title_contains:
        tickets_resp = [t for t in tickets_resp if title_contains.lower() in t["title"].lower()]

    if not tickets_resp:
        return f"No tickets matched the criteria for email {email}"

    ticket_to_update = tickets_resp[0]
    ticket_id = ticket_to_update["id"]

    payload = {
        "ticket_id": ticket_id,
        "title": new_title,
        "description": new_description,
        "priority": new_priority,
        "status": new_status
    }
    payload = {k: v for k, v in payload.items() if v is not None}

    if not payload:
        return "❌ No fields provided to update."

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "http://192.168.1.70:8000/sync_tickets/create_tickets",
            json=payload,
            headers=headers
        )
    response.raise_for_status()
    return response.json()

from langchain_core.tools import tool
import httpx
import json
from app.auth import get_admin_token

# @tool
# async def delete_ticket(ticket_id: str):
#     """
#     Delete a ticket by ticket_id using the existing CRM API.

#     RULES:
#     - Requires exact ticket_id.
#     - Calls backend DELETE API.
#     - Returns API response as JSON.
#     - If ticket_id is missing, return error.
#     """

#     if not ticket_id or not str(ticket_id).strip():
#         return {"status": 400, "detail": "ticket_id is required"}

#     token = await get_admin_token()

#     headers = {
#         "Authorization": f"Bearer {token}",
#         "Content-Type": "application/json"
#     }

#     async with httpx.AsyncClient(timeout=30) as client:
#         response = await client.request(
#             "DELETE",
#             "http://192.168.1.70:8000/sync_tickets/ticket_delete",
#             data=json.dumps({"ticket_id": ticket_id}),
#             headers=headers
#         )

#     try:
#         return response.json()
#     except Exception:
#         return {
#             "status": response.status_code,
#             "detail": "Failed to parse API response"
#         }



@tool
async def delete_ticket(ticket_id: str):
    """
    Delete a ticket using Project 2 API.
    Requires ticket_id.
    """

    if not ticket_id or not str(ticket_id).strip():
        return {"status": 400, "detail": "ticket_id is required"}
    token = await get_admin_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.request(
            "DELETE",
            "http://192.168.1.70:8000/sync_tickets/ticket_delete",  # ADD prefix here if exists
            json={"ticket_id": int(ticket_id)},
            headers=headers
        )

    try:
        return response.json()
    except Exception:
        return {
            "status": response.status_code,
            "detail": "Invalid response from Project 2"
        }