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

        
# # app/streamlit_app.py
# import streamlit as st
# import requests
# import asyncio
# from auth import get_admin_token  # async token fetch
# from functools import partial

# # ---------------- CONFIG ----------------
# CHAT_API_URL = "http://192.168.1.70:5001/chat"
# PROJECT1_LOGIN_API = "http://192.168.1.70:5000/auth/login"  # Project1 API

# st.set_page_config(page_title="AI CRM Assistant", layout="centered")

# # ---------------- SESSION INIT ----------------
# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False
# if "messages" not in st.session_state:
#     st.session_state.messages = []
# if "token" not in st.session_state:
#     st.session_state.token = None
# if "email" not in st.session_state:
#     st.session_state.email = None
# if "role" not in st.session_state:
#     st.session_state.role = None


# # ---------------- SYNC WRAPPER FOR ASYNC TOKEN ----------------
# def get_user_token_sync(email: str) -> str:
#     """
#     Run the async get_user_token inside Streamlit safely.
#     """
#     try:
#         loop = asyncio.get_event_loop()
#     except RuntimeError:
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)

#     return loop.run_until_complete(get_admin_token(email))


# # ---------------- LOGIN FUNCTION ----------------
# def login(email: str, password: str):
#     """
#     Login via Project1 API, store token in Redis, then fetch it dynamically.
#     """
#     if not email or not password:
#         st.warning("Please enter email and password")
#         return False

#     # Call Project1 login API
#     try:
#         res = requests.post(
#             PROJECT1_LOGIN_API,
#             json={"email": email, "password": password},
#             timeout=10
#         )
#         if res.status_code != 200:
#             st.error(f"Login failed: {res.json().get('error','Unknown error')}")
#             return False

#         st.success("Login API successful ✅")
#     except requests.exceptions.RequestException:
#         st.error("Project1 API not reachable")
#         return False

#     # Fetch token dynamically from Redis
#     try:
#         st.session_state.token = get_user_token_sync(email)
#     except Exception as e:
#         st.error(f"Token fetch failed: {e}")
#         return False

#     st.session_state.email = email
#     st.session_state.logged_in = True
#     st.session_state.role = res.json().get("role", "user")
#     return True


# # ---------------- LOGIN PAGE ----------------
# def login_page():
#     st.title("🔐 Login to AI CRM Assistant")
#     email = st.text_input("📧 Email")
#     password = st.text_input("🔑 Password", type="password")
#     if st.button("Login", use_container_width=True):
#         if login(email, password):
#             st.rerun()


# # ---------------- CHAT PAGE ----------------
# def chat_page():
#     st.sidebar.markdown("## 🤖 AI CRM Assistant")
#     st.sidebar.markdown(f"👤 **{st.session_state.email}**")
#     st.sidebar.caption(f"Role: {st.session_state.role}")
#     st.sidebar.divider()

#     if st.sidebar.button("🚪 Logout"):
#         st.session_state.clear()
#         st.rerun()

#     st.title("🤖 AI CRM Assistant")

#     # Display chat history
#     for msg in st.session_state.messages:
#         with st.chat_message(msg["role"]):
#             st.markdown(msg["content"])

#     # User input
#     user_input = st.chat_input("Ask me about tickets, LLM, or other tasks...")

#     if user_input:
#         st.session_state.messages.append({"role": "user", "content": user_input})
#         with st.chat_message("user"):
#             st.markdown(user_input)

#         bot_reply = ""
#         try:
#             with st.spinner("Thinking..."):
#                 payload = {
#                     "user_id": st.session_state.email,
#                     "message": user_input
#                 }

#                 response = requests.post(
#                     CHAT_API_URL,
#                     json=payload,
#                     headers={"Authorization": f"Bearer {st.session_state.token}"},
#                     timeout=30
#                 )

#                 response.raise_for_status()
#                 bot_reply = response.json().get("reply", "❌ No response")
#         except Exception as e:
#             bot_reply = f"❌ Error:\n{e}"

#         st.session_state.messages.append({"role": "assistant", "content": bot_reply})
#         with st.chat_message("assistant"):
#             st.markdown(bot_reply)


# # ---------------- MAIN APP FLOW ----------------
# if not st.session_state.logged_in:
#     login_page()
# else:
#     chat_page()
