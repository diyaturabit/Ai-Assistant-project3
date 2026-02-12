from langchain_core.tools import tool
from app.auth import get_admin_token
import requests
import httpx

# @tool
# async def searching(query:str):
#     """
#     Search customers and tickets in the CRM using a keyword.
#     Use this when the user asks to search, find, lookup, or query records.
#     """
#     if not query.strip():
#         return {
#             "error":"Search input is required"
#         }
#     token=await get_admin_token()
#     print(f"Searching ticket token:",token)

#     headers={
#         "Authorization":f"Bearer {token}"
#     }
#     # params={"q":query}
#     async with httpx.AsyncClient(timeout=30) as client:
#         response = await client.get(
#             "http://192.168.1.70:5000/search/search",
#             params={"q":query},
#             headers=headers
#         )
#         response.raise_for_status()
#         data=response.json()
#         print(f"Searching output:",data)

#     return data

# from langchain_core.tools import tool
# from app.auth import get_admin_token
# import httpx

# @tool
# async def searching(email: str):
#     """
#     Search for a customer by email and return their details + tickets.
#     """
#     if not email.strip():
#         return {"error": "Customer email is required"}

#     token = await get_admin_token()
#     headers = {"Authorization": f"Bearer {token}"}

#     async with httpx.AsyncClient(timeout=30) as client:
#         response = await client.get(
#             "http://192.168.1.70:5000/search/search",
#             params={"q": email},
#             headers=headers
#         )
#         response.raise_for_status()
#         data = response.json()

#     # Find the customer
#     customer = next(
#         (c for c in data.get("customers", []) if c.get("email", "").lower() == email.lower()), 
#         None
#     )
#     if not customer:
#         return {"message": f"No customer found with email {email}"}

#     customer_id = customer["id"]

#     # Filter tickets by customer_id
#     tickets = [
#         t for t in data.get("tickets", [])
#         if t.get("customer_id") == customer_id
#     ]

#     return {
#         "customer": customer,
#         "tickets": tickets[:15]  # limit to first 15 tickets
#     }


from langchain_core.tools import tool
from app.auth import get_admin_token
import httpx

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
            "http://192.168.1.70:5000/search/search",
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
