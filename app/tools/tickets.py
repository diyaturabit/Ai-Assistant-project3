from langchain_core.tools import tool
from app.auth import get_admin_token
import httpx
import requests
from config import PROJECT2_URL

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
            f"{PROJECT2_URL}/sync_tickets/tickets_get",
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
            f"{PROJECT2_URL}/sync_tickets/tickets_get",
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
            f"{PROJECT2_URL}/sync_tickets/create_tickets",
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

from typing import Optional
from langchain.tools import tool

@tool("update_ticket", description="Update a ticket by ticket_id")
async def update_ticket(
    ticket_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
):
    """
    Update an existing ticket using its ticket ID.

    PARAMETERS:
    - ticket_id (int): The unique ID of the ticket to update. (Required)
    - title (str, optional): New title for the ticket.
    - description (str, optional): New description for the ticket.
    - priority (str, optional): New priority level (e.g., Low, Medium, High).
    - status (str, optional): New status (e.g., Open, In Progress, Closed).

    RULES:
    - ticket_id is required.
    - Only update the fields that are explicitly provided.
    - Do not send fields that are None.
    - At least one field must be provided for update.
    - This tool updates a single ticket only.

    RETURNS:
    - JSON response from the ticket update API.
    - Should confirm:
        - ticket_id
        - updated fields
        - update status

    USE CASE:
    Call this tool only after the user has selected a specific ticket ID
    and clearly mentioned which fields to update.
    """
    payload = {
        "ticket_id": ticket_id,
        "title": title,
        "description": description,
        "priority": priority,
        "status": status,
    }

    payload = {k: v for k, v in payload.items() if v is not None}

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.put(
            f"{PROJECT2_URL}/sync_tickets/update_ticket",
            json=payload
        )

    return response.json()



@tool("delete_ticket", description="Delete a ticket by ticket_id")
async def delete_ticket(ticket_id: str):
    """
    Deletes a ticket from the system.

    Rules:
    - ticket_id is required
    - Returns deletion status
    - Indicates if HubSpot ticket was deleted
    """

    if not ticket_id:
        return {
            "error": "ticket_id is required"
        }

    url = f"{PROJECT2_URL}/sync_tickets/ticket_delete"   # change port if needed

    payload = {
        "ticket_id": ticket_id
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.delete(url, json=payload)
    # if response.status_code != 200:
    #     return {
    #         "error": f"Failed to delete ticket. Status code: {response.status_code}",
    #         "details": response.text
    #     }
    if response.status_code != 200:
        print("STATUS:", response.status_code)
        print("RESPONSE TEXT:", response.text)
        return {
            "error": f"Failed to delete ticket. Status code: {response.status_code}",
            "details": response.text
        }
    data = response.json()
    return {
        "status": data.get("status"),
        "ticket_id": data.get("ticket_id"),
        "hubspot_deleted": data.get("hubspot_deleted")
    }
