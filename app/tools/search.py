from langchain_core.tools import tool
from app.auth import get_admin_token

import httpx
from config import PROJECT1_URL


@tool
async def searching(query: str):
    """
    Tool: searching
    Purpose:
    - Search for customers and tickets in the CRM using a keyword, email, or customer name.
    - Returns the first 10 matching customers and tickets.
    - If nothing is found, returns empty lists and a clear message.
    
    Input:
    - query (string): The search keyword or phrase (e.g., customer name, email, ticket title or description).
    
    Output:
    - JSON object containing:
        • customers: list of matching customers
        • tickets: list of matching tickets
    - If nothing is found:
        • Return {"customers": [], "tickets": [], "message": "No customers or tickets found for '<query>'"}
    
    Rules for LLM:
    - Call this tool only when the user explicitly asks to "search", "find", "lookup", "query", or similar phrases.
    - Pass the search query **exactly as provided** by the user.
    - Respect output format requested by user:
        • Table → show first 10 customers/tickets in a readable table with proper columns.
            - Customers table: ID | Name | Email | Company | Age
            - Tickets table: ID | Customer Email | Title | Priority | Status | Customer | Created At
        • JSON → return pure JSON object as above.
    - Limit output to the first 10 results per category.
    - Include a message if no results are found.
    - Do not simulate results — always return actual tool output.
    - Ask for clarification if the query is empty or ambiguous.

    """
    if not query.strip():
        return {"error": "Search query is required"}

    token = await get_admin_token()
    print(f"Searching token :",token)
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            f"{PROJECT1_URL}/search/search",
            params={"q": query},
            headers=headers
        )
        print(f"Response:",response)
        response.raise_for_status()
        data = response.json()

    customers = data.get("customers", [])
    tickets = data.get("tickets", [])

    result = {
        "customers": customers,
        "tickets": tickets
    }

    if not customers and not tickets:
        result["message"] = f"No customers or tickets found for '{query}'"

    return result
