📘 AI CRM Assistant – API Documentation (Project 3)
🌐 Base URL
http://192.168.1.70:5001

🔐 Authentication

All requests require a valid token (if authentication is implemented).

Header Format
Authorization: Bearer <access_token>

🤖 Chat API – Single Endpoint
📌 POST /chat
Description

This is the only API endpoint.
It acts as a central hub for the AI CRM Assistant. Based on the user’s natural language query, it:

Calls Project 2 APIs dynamically (tickets/customers)

Extracts parameters from user input

Generates AI responses using LLM tool-calling

Returns structured output

All operations (fetching tickets, creating/updating customers, summaries) are handled through this single endpoint.

Request Body
{
  "message": "show me tickets of last week",
  "conversation_id": 1
}

Field	Type	Required	Description
message	string	✅	User query in natural language
conversation_id	integer	✅	Conversation ID to maintain chat history
Response Example
{
  "reply": "Here are the open tickets from last week for diyab12@gmail.com...",
  "conversation_id": 1
}


reply → AI-generated text with structured information

conversation_id → identifier for the conversation thread

Supported Queries

The /chat endpoint supports:

Finding tickets by email

Viewing tickets for a specific time period (today, last week, this month)

Updating tickets

Viewing open/closed tickets

Creating/updating customers

Returning summaries (total tickets, total customers)

Example Queries:

find ticket of diyab12@gmail.com
show me tickets of last week
update ticket of diyab12@gmail.com
65 title to okaydkjfdkdj
find ticket for shrivasini@gmail.com
view ticket open ticket of last week
how many tickets arwe there total tickets?
total customers?
User input: Hello, how can you help me?
User input: show all tickets
User input: filter all high priority tickets
User input: show all the tickets from 30 Jan 2026 to today


Behavior

Parses created_at to datetime objects for filtering

Applies timezone-aware calendar filtering

Limits output to 15 items for large queries

Generates structured summaries

Uses tool-calling to dynamically call the correct backend functions

Error Handling
Status Code	Meaning
400	Bad request / invalid input
401	Unauthorized (if auth enabled)
500	Internal server error
Conversation & Memory

Uses ChatGPT-style conversation memory stored in DB

Messages are stored in a messages table under a conversation_id

Each conversation stores all user queries and AI responses

Example Flow

User sends: "show me tickets of last week for diyab12@gmail.com"

/chat endpoint receives the query

LLM extracts parameters → calls fetch_tickets from Project 2 API

AI formats response and returns:

Here are 12 open tickets from last week for diyab12@gmail.com...


Conversation history is stored in DB for future reference

Tech Stack

Backend: FastAPI

AI: LLM Tool Calling

Frontend: Streamlit

Database: PostgreSQL / MySQL (conversations + messages)

HTTP Client: httpx

Date Handling: datetime + zoneinfo

👩‍💻 Maintainer

Diya Bosamiya
AI CRM Assistant – Project 3