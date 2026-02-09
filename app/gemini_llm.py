# from langchain_google_genai import ChatGoogleGenerativeAI
# from dotenv import load_dotenv
# import os
# load_dotenv()
# def get_gemini_llm():
#     return ChatGoogleGenerativeAI(
#         model="gemini-2.0-flash",
#         google_api_key=os.getenv("GEMINI_API_KEY"),
#         temperature=0.2,
#     )

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

llm = ChatGroq(
    model_name="qwen/qwen3-32b", 
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7
)


messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="I am diyaa")
]

response = llm.invoke(messages)

print(response.content)
