from langchain_core.tools import tool
from app.auth import get_admin_token
import requests
import httpx

@tool
async def searching(query:str):
    """
    Search customers and tickets in the CRM using a keyword.
    Use this when the user asks to search, find, lookup, or query records.
    """
    if not query.strip():
        return {
            "error":"Search input is required"
        }
    token=await get_admin_token()
    print(f"Searching ticket token:",token)

    headers={
        "Authorization":f"Bearer {token}"
    }
    # params={"q":query}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            "http://192.168.1.70:5000/search/search",
            params={"q":query},
            headers=headers
        )
        response.raise_for_status()
        data=response.json()
        print(f"Searching output:",data)

    return data