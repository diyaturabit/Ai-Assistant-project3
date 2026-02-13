# from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
# load_dotenv()
# def get_gemini_llm():
#     return ChatGoogleGenerativeAI(
#         model="gemini-2.0-flash",
#         google_api_key=os.getenv("GEMINI_API_KEY"),
#         temperature=0.2,
#     )


from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

def get_groq_llm():
    return ChatGroq(
        model_name="moonshotai/kimi-k2-instruct-0905",  # Your Groq model
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2,
    )

