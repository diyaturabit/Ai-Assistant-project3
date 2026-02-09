# from fastapi import FastAPI
# from dotenv import load_dotenv

# from schemas.chat import ChatRequest
# from agents.agents import agent_executor
# from memory.redis_memory import save_message,get_history

# load_dotenv()

# app = FastAPI(title="AI CRM Assistant")

# @app.post("/chat")
# async def chat(req: ChatRequest):
#     # get previous chat history
#     chat_history = get_history(req.user_id)

#     # call LangChain agent
#     result = agent_executor.invoke({
#         "input": req.message,
#         "chat_history": chat_history
#     })

#     # save conversation
#     save_message(req.user_id, req.message)
#     save_message(req.user_id, result["output"],role="ai")

#     return {
#         "reply": result["output"]
#     }


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="192.168.1.70", port=5001, reload=True)


# from fastapi import FastAPI
# from dotenv import load_dotenv
# import app.schemas.chat
# from app.schemas.chat import ChatRequest
# from app.agents.agents import agent   
# load_dotenv()
# import os
# app = FastAPI(title="AI CRM Assistant")
# print(os.getenv("GEMINI_API_KEY"))

# @app.post("/chat")
# async def chat(req: ChatRequest):
#     result = agent.invoke(
#         {
#             "messages": [
#                 {"role": "user", "content": req.message}
#             ]
#         }
#     )
#     print(f"Result",result)
#     return {
#         "reply": result
#     }


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="192.168.1.70", port=5001)


from fastapi import FastAPI

from dotenv import load_dotenv
from app.schemas.chat import ChatRequest
from app.agents.agents import agent
import json
from langchain_core.messages import AIMessage, ToolMessage

load_dotenv()

app = FastAPI(title="AI CRM Assistant")


def parse_agent_result(result):
    """Extract readable AI message or format tickets table."""
    if hasattr(result, "messages"):
        for msg in result.messages:
            if isinstance(msg, AIMessage):
                return msg.content
            if isinstance(msg, ToolMessage):
                try:
                    data = json.loads(msg.content)
                    if "tickets" in data:
                        # Format tickets in table
                        table = "ID | Customer | Priority | Status | Title\n"
                        table += "---|----------|---------|--------|------\n"
                        for t in data["tickets"]:
                            table += f"{t['id']} | {t['customer_name']} | {t['priority']} | {t['status']} | {t['title']}\n"
                        return table
                    return str(data)
                except:
                    return str(msg.content)
    return str(result)

@app.post("/chat")
async def chat(req: ChatRequest):
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": req.message}]}
    )

    reply = parse_agent_result(result)
    return {"reply": reply}


# @app.post("/chat")
# async def chat(req: ChatRequest):
#     # Run synchronous agent in a threadpool to avoid blocking
#     result = await run_in_threadpool(
#         lambda: agent.invoke({"messages": [{"role": "user", "content": req.message}]})
#     )
#     reply = parse_agent_result(result)
#     return {"reply": reply}

