from langchain_core.tools import tool
from app.auth import get_admin_token
import httpx
import requests
from config import PROJECT2_URL
from app.exception_handling import handle_exception
@tool
async def fetch_tickets(status: str | None = None, priority: str | None = None):
    """
    Fetch tickets from the CRM system.

    RULES:
    - Fetch only the first 15 tickets to prevent large responses.
    ALWAYS return tickets with ONLY the following fields:
    - id
    - title
    - customer_email
    - status
    - priority
    - created_at

    - Include summary:
        - Total tickets matching the query
        - Number of open tickets
        - Number of closed tickets
        - Number displayed
    - If more than 15 tickets exist, include note:
        "Showing first 15 tickets. There are <X> more tickets available."
    - Supports optional filters:
        - status: "open" ,"Inprogress" "closed"
        - priority: "Low", "Medium", "High"
        - time filters (optional): today, yesterday, this week, last week, last month, between <date1> and <date2>
    - Returns a formatted list of tickets based on requested output format:
        - JSON, table, or human-readable summary
    - The LLM should call this tool **only when a ticket view or search query is detected**.
    """

    try:
        print("Fetching tickets...")

        params = {}
        if status:
            params["status"] = status
        if priority:
            params["priority"] = priority

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(
                f"{PROJECT2_URL}/sync_tickets/tickets_get",
                params=params
            )
            response.raise_for_status()

        return response.json()

    except Exception as e:
        return handle_exception(e)

    finally:
        print("fetch_tickets execution completed.")


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
    - If more than 15 tickets exist, add:
        "Showing first 15 tickets. There are <X> more tickets available."
    - If no tickets are found, return a clear message:
        "No tickets found for this customer."
    - Supports optional time filters (today, yesterday, this week, last week, last month, between <date1> and <date2>)
    - LLM should call this tool **only when a user requests tickets for a specific email**.
    """

    try:
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

    except Exception as e:
        return handle_exception(e)

    finally:
        print("fetch_tickets_by_email execution completed.")


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
    - Ask for missing required fields one by one (dynamic interaction).
    - Normalize priority internally (capitalize first letter).
    - Only call tool if all required fields are present.
    - Returns a clear confirmation including:
        - Internal DB ticket ID
        - HubSpot ticket ID
    - LLM should call this tool **only when creating a new ticket**.
    - Supports user-requested output format (JSON, table, human-readable summary).
    """

    try:
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

    except Exception as e:
        return handle_exception(e)

    finally:
        print("create_ticket execution completed.")

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
    - ticket_id (int): Required. The unique ID of the ticket to update.
    - title (str, optional): New title for the ticket.
    - description (str, optional): New description for the ticket.
    - priority (str, optional): New priority level (Low, Medium, High).
    - status (str, optional): New status (Open, In Progress, Closed).

    RULES:
    - Only update fields that are explicitly provided (ignore None values).
    - At least one field must be provided.
    - Returns confirmation with:
        - ticket_id
        - updated fields
        - update status
    - LLM should call this tool **only after the user has selected a ticket ID and specified the fields to update**.
    """

    try:
        payload = {
            "ticket_id": ticket_id,
            "title": title,
            "description": description,
            "priority": priority,
            "status": status,
        }

        payload = {k: v for k, v in payload.items() if v is not None}

        if len(payload) <= 1:
            return {"error": "At least one field must be provided for update."}

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.put(
                f"{PROJECT2_URL}/sync_tickets/update_ticket",
                json=payload
            )
            response.raise_for_status()

        return response.json()

    except Exception as e:
        return handle_exception(e)
    
    finally:
        print("update_ticket execution completed.")


@tool("delete_ticket", description="Delete a ticket by ticket_id")
async def delete_ticket(ticket_id: str):
    """
    Tool: delete_ticket
    Purpose:
    - Delete a ticket from the CRM system using its `ticket_id`.
    - Deletes the corresponding HubSpot ticket if it exists.
    - Returns a structured status message including:
        • ticket_id
        • deletion status
        • whether HubSpot ticket was deleted
    
    Input:
    - ticket_id (string) → required. The unique ID of the ticket to delete.
    
    Output:
    - JSON object containing:
        • status → deletion status ("success" or "error")
        • ticket_id → the ticket that was deleted
        • hubspot_deleted → whether HubSpot ticket was removed (true/false)
    - If `ticket_id` is missing or deletion fails:
        • Return a clear error message with details
    
    Rules for LLM:
    - Only call this tool when the user explicitly asks to delete or remove a ticket, e.g.:
        • "delete ticket 123"
        • "remove ticket 456"
        • "delete ticket by id 789"
    - Extract numeric `ticket_id` from the user query.
    - If `ticket_id` is not provided in the query, ask the user: "Please provide the ticket ID."
    - Never simulate deletion results — always use the tool’s actual response.
    - Respect output format requested by the user:
        • Human-readable → "✅ Ticket deleted successfully | Ticket ID: X | HubSpot Deleted: True/False"
        • JSON → structured JSON with status, ticket_id, and hubspot_deleted fields.
    - Do NOT return raw API responses directly.

    """
    try:
        if not ticket_id:
            return {"error": "ticket_id is required"}

        token = await get_admin_token()
        headers = {"Authorization": f"Bearer {token}"}

        url = f"{PROJECT2_URL}/sync_tickets/ticket_delete"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                "DELETE",
                url,
                json={"ticket_id": ticket_id},
                headers=headers
            )
            response.raise_for_status()

        data = response.json()

        return {
            "status": data.get("status"),
            "ticket_id": data.get("ticket_id"),
            "hubspot_deleted": data.get("hubspot_deleted")
        }

    except Exception as e:
        return handle_exception(e)

    finally:
        print("delete_ticket execution completed.")