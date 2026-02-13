
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from app.agents.prompts import system_prompt


from app.tools.tickets import fetch_tickets,create_ticket,fetch_tickets_by_email,delete_ticket,update_ticket
from app.tools.customers import fetch_customers,create_customers,delete_customer
from app.tools.search import searching
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
from app.gemini_llm import get_groq_llm
load_dotenv()


tools = [fetch_tickets,
         create_ticket,
         searching,
         fetch_customers,
         create_customers,
         delete_customer,
         fetch_tickets_by_email,
         delete_ticket,
         update_ticket
        ]


# Create agent (MODERN LANGCHAIN)
agent = create_agent(
    model=get_groq_llm(),
    tools=tools,
    system_prompt=system_prompt
)
