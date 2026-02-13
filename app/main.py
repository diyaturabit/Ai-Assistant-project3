
from fastapi import FastAPI
# from dotenv import load_dotenv
from app.schemas.chat import ChatRequest
from app.agents.agents import agent
import json
from langchain_core.messages import AIMessage, ToolMessage
from fastapi.concurrency import run_in_threadpool

# load_dotenv()

app = FastAPI(title="AI CRM Assistant")



def parse_agent_result(result: dict):
    """
    Extract final AI response from LangChain agent result (DICT-based).
    """

    if not result or "messages" not in result:
        return "❌ No response generated."

    final_ai_message = None
    last_tool_message = None

    # Walk messages in order
    for msg in result["messages"]:
        if isinstance(msg, ToolMessage):
            last_tool_message = msg.content

        if isinstance(msg, AIMessage) and msg.content.strip():
            final_ai_message = msg.content

    # ✅ Priority 1: Final AI response
    if final_ai_message:
        return final_ai_message

    # ✅ Priority 2: Tool fallback (JSON / table)
    if last_tool_message:
        try:
            data = json.loads(last_tool_message)
            if "tickets" in data:
                rows = ["ID | Title | Priority | Status | Customer"]
                rows.append("-" * 50)
                for t in data["tickets"]:
                    rows.append(
                        f"{t['id']} | {t['title']} | "
                        f"{t['priority']} | {t['status']} | "
                        f"{t['customer_name']}"
                    )
                return "\n".join(rows)
            return json.dumps(data, indent=2)
        except Exception:
            return str(last_tool_message)

    return "❌ No response generated."


@app.post("/chat")
async def chat(req: ChatRequest):
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": req.message}]}
    )

    reply = parse_agent_result(result)
    return {"reply": reply}
