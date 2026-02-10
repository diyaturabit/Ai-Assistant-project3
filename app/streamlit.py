import streamlit as st
import requests

# ---------------- CONFIG ----------------
API_URL = "http://192.168.1.70:5001/chat"  # change if needed
st.set_page_config(page_title="AI CRM Assistant", layout="centered")

# ---------------- UI ----------------
st.title("🤖 AI CRM Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_input = st.chat_input("Ask me about tickets...")
print(f"User input:",user_input)
if user_input:
    # Show user message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call API
    try:
        with st.spinner("Thinking..."):
            response = requests.post(
                API_URL,
                json={"message": user_input},
                timeout=30
            )

        response.raise_for_status()
        data = response.json()

        bot_reply = data.get("reply", "❌ No response")

    except Exception as e:
        bot_reply = f"❌ Error calling API:\n\n{e}"

    # Show bot response
    st.session_state.messages.append(
        {"role": "assistant", "content": bot_reply}
    )
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
