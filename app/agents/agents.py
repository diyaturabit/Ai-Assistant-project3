

from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from app.agents.prompts import system_prompt
from langchain_groq import ChatGroq
# from app.gemini_llm import get_gemini_llm
from app.tools.tickets import fetch_tickets,create_ticket
from app.tools.customers import fetch_customers,create_customers,delete_customer
from app.tools.search import searching
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
load_dotenv()


# def get_gemini_llm():
#     return ChatGoogleGenerativeAI(
#         model="gemini-2.5-pro",
#         google_api_key=os.getenv("GEMINI_API_KEY"),
#         temperature=0.2,
#     )

def get_groq_llm():
    return ChatGroq(
        model_name="qwen/qwen3-32b",  # Your Groq model
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2,
    )


tools = [fetch_tickets,create_ticket,searching,fetch_customers,create_customers,delete_customer]


# Create agent (MODERN LANGCHAIN)
agent = create_agent(
    model=get_groq_llm(),
    tools=tools,
    system_prompt=system_prompt
)
