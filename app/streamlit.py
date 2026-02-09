# import streamlit as st
# import json
# import requests  # for calling /chat API if needed

# st.title("🤖 AI CRM Assistant")

# # No chat history persistence
# user_input = st.text_input("Type your message here:")

# if st.button("Send") and user_input:
#     # Display user message
#     st.markdown(
#         f"<div style='text-align:right; background-color:#DCF8C6; padding:8px; border-radius:10px; margin:5px 0'><b>You:</b> {user_input}</div>",
#         unsafe_allow_html=True
#     )

#     try:
#         # --- Option 1: Direct LangChain agent call ---
#         # from agents.agents import agent
#         # result = agent.invoke({"messages": [{"role": "user", "content": user_input}]})
#         # ai_reply = result.content  # basic response

#         # --- Option 2: Call FastAPI /chat endpoint ---
#         response = requests.post(
#             "http://192.168.1.70:5001/chat",
#             json={"user_id": "user_1", "message": user_input},
#             timeout=30
#         )
#         api_result = response.json()
#         ai_reply = api_result.get("reply", "No response from AI.")

#         # --- Process tickets for table display ---
#         try:
#             # If AI returned ticket JSON
#             data = json.loads(ai_reply)
#             tickets = data.get("tickets", [])

#             if tickets:
#                 st.write("### Tickets")
#                 # Create table
#                 table_data = []
#                 for t in tickets:
#                     table_data.append({
#                         "Ticket ID": t.get("id"),
#                         "Customer": t.get("customer_name"),
#                         "Title": t.get("title"),
#                         "Priority": t.get("priority"),
#                         "Status": t.get("status")
#                     })
#                 st.table(table_data)
#             else:
#                 st.markdown(f"<div style='background-color:#F1F0F0; padding:8px; border-radius:10px;'>{ai_reply}</div>", unsafe_allow_html=True)
#         except Exception:
#             # Not ticket data, normal AI reply
#             st.markdown(f"<div style='background-color:#F1F0F0; padding:8px; border-radius:10px;'>{ai_reply}</div>", unsafe_allow_html=True)

#     except Exception as e:
#         st.markdown(f"<div style='background-color:#F1F0F0; padding:8px; border-radius:10px;'>Error: {str(e)}</div>", unsafe_allow_html=True)

import streamlit as st
import requests

st.set_page_config(page_title="AI CRM Assistant", page_icon="🤖")
st.title("🤖 AI CRM Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

user_input = st.text_input("Type your message here:")

if st.button("Send") and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        # Call FastAPI chat endpoint
        response = requests.post(
            "http://192.168.1.70:5001/chat",
            json={"message": user_input},
            timeout=60
        )
        reply = response.json().get("reply", "No reply")
    except Exception as e:
        reply = f"Error: {str(e)}"

    st.session_state.messages.append({"role": "bot", "content": reply})

# Display chat messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f"<div style='text-align:right; background-color:#DCF8C6; padding:8px; border-radius:10px; margin:5px 0'>{msg['content']}</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div style='text-align:left; background-color:#F1F0F0; padding:8px; border-radius:10px; margin:5px 0'>{msg['content']}</div>",
            unsafe_allow_html=True
        )
