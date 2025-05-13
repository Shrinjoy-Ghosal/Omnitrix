import streamlit as st
import requests

# FastAPI backend URL
FASTAPI_URL = "http://localhost:8000"  # Replace with actual backend URL

# Maintain chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

st.title("Omnitrix Chatbot 🤖")

# User input
user_input = st.text_input("Ask Omnitrix something:")

if user_input:  # ✅ Ensure input isn't empty
    # Send query to FastAPI backend
    response = requests.post(f"{FASTAPI_URL}/chatbot", json={"query": user_input})

    if response.status_code == 200:
        chatbot_reply = response.json().get("answer", "Omnitrix is thinking... 🤖")
        
        # ✅ Remove `[INST]` markers & repeated question
        chatbot_reply = chatbot_reply.replace("[INST]", "").replace("[/INST]", "").strip()
        
        if user_input in chatbot_reply:
            chatbot_reply = chatbot_reply.replace(user_input, "").strip()  # ✅ Fully remove repetition
    else:
        chatbot_reply = "Error connecting to backend 🚨"

    # ✅ Add to chat history correctly
    st.session_state["chat_history"].append({"user": user_input, "bot": chatbot_reply})

    # Display response
    st.write(f"**Omnitrix:** {chatbot_reply}")

# Show chat history
st.subheader("Chat History 📜")
for chat in st.session_state["chat_history"]:
    st.write(f"👤 **You:** {chat['user']}")
    st.write(f"🤖 **Omnitrix:** {chat['bot']}")