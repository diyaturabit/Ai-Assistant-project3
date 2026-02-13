from langchain_core.tools import tool
from app.auth import get_admin_token

import httpx
from config import PROJECT1_URL


@tool
async def searching(query: str):
    """
    Search for customers and tickets using a keyword, email, or name.

    INPUT:
    - query (str): Keyword to search (customer name, email, or ticket info)

    OUTPUT:
    - JSON containing:
        - customers: list of matching customers
        - tickets: list of matching tickets
    - Returns first 10 customers and tickets
    - If nothing is found, returns empty lists with message
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
