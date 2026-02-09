# from tools.tickets import fetch_tickets
# from gemini_llm import get_gemini_llm
# from agents.prompts import system_prompt
# from langchain.agents import create_tool_calling_agent, AgentExecutor

# tools=[
#     fetch_tickets,
# ]
# agent = create_tool_calling_agent(
#     llm=get_gemini_llm(),
#     tools=tools,
#     prompt=system_prompt
# )

# agent_executor = AgentExecutor(
#     agent=agent,
#     tools=tools,
#     verbose=True
# )

from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from app.agents.prompts import system_prompt
from langchain_groq import ChatGroq
# from app.gemini_llm import get_gemini_llm
from app.tools.tickets import fetch_tickets,create_ticket

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


tools = [fetch_tickets,create_ticket]


# Create agent (MODERN LANGCHAIN)
agent = create_agent(
    model=get_groq_llm(),
    tools=tools,
    system_prompt=system_prompt
)
