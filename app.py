import google.generativeai as genai
import streamlit as st
import time

# --- 1. SECURE API KEY CONFIGURATION ---
# Use Streamlit's secrets management for the API key
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception as e:
    st.error("API Key not found or invalid. Please add it to your Streamlit secrets.")
    st.stop()


# --- 2. SYSTEM INSTRUCTION FOR SPECIALIZATION ---
# This is the core instruction that customizes the chatbot's behavior.
# It defines the chatbot's persona, its limited scope of knowledge, and the exact refusal message.
system_instruction = (
    "You are a specialized AI assistant named 'Aushadi Veda'. "
    "Your sole purpose is to provide medicinal information exclusively about the following systems: "
    "Ayurveda, Yoga, Homeopathy, Siddha, and Unani. "
    "You can answer questions about medicinal plants, herbs, remedies, and principles ONLY within these systems. "
    "If a user asks about anything outside of these specific domains (such as allopathic medicine, modern drugs, general knowledge, chemistry, or any other topic), "
    "you MUST respond with the exact phrase: "
    "'I suggest this types details medicials information only ayurvedic or yoga, hameopathy ,siddha, unani' "
    "and nothing else. Do not apologize or explain further."
)


# --- 3. MODEL AND GENERATION CONFIGURATION ---
generation_config = {
    "temperature": 1, # Slightly lower for more factual responses
    "top_p": 1,
    "top_k": 100,
    "max_output_tokens": 819200, # Increased for potentially detailed answers
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
    system_instruction=system_instruction, # Applying the custom rules here
)


# --- 4. RETRY FUNCTION FOR RATE LIMIT HANDLING ---
def send_with_retry(chat_session, prompt, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = chat_session.send_message(prompt)
            return response
        except Exception as e:
            if "RATE_LIMIT_EXCEEDED" in str(e):
                wait_time = 2 ** attempt  # Exponential backoff
                st.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                raise e
    raise Exception("Max retries exceeded due to rate limiting. Please request a quota increase at https://cloud.google.com/docs/quotas/help/request_increase or use a different API key with available quota.")


# --- 5. PROFESSIONAL UI SETUP ---
st.set_page_config(
    page_title="Aushadi Veda - AI Medical Assistant",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-container {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: right;
    }
    .assistant-message {
        background: white;
        color: #333;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        padding: 1rem;
        border-top: 1px solid #e9ecef;
        z-index: 1000;
    }
    .sidebar-content {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #667eea;
        padding: 0.5rem 1rem;
    }
    .stTextInput > div > div > input:hover {
        border-color: #667eea !important;
        box-shadow: none !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        height: 100%;
        align-self: stretch;
    }
    .input-row {
        display: flex;
        align-items: stretch;
        gap: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🌿 Aushadi Veda</h1>
    <p>AI-Powered Traditional Medicine Assistant</p>
    <p style="font-size: 0.9em;">Specialized in Ayurveda, Yoga, Homeopathy, Siddha, and Unani</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with professional design
with st.sidebar:
    st.markdown("""
    <div class="sidebar-content">
        <h3>🧠 About Aushadi Veda</h3>
        <p>Your intelligent companion for traditional medicinal knowledge. Get accurate information about:</p>
        <ul>
            <li>🌱 Medicinal Plants & Herbs</li>
            <li>🧘 Yoga Practices</li>
            <li>💊 Homeopathic Remedies</li>
            <li>🏺 Siddha Medicine</li>
            <li>🌙 Unani Medicine</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📊 Statistics")
    if "messages" in st.session_state:
        user_msgs = len([m for m in st.session_state.messages if m["role"] == "user"])
        st.metric("Questions Asked", user_msgs)

    st.markdown("---")
    st.markdown("### 🔄 Quick Actions")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.rerun()

    if st.button("📖 Help"):
        st.info("Ask me about traditional medicinal systems! I specialize in Ayurveda, Yoga, Homeopathy, Siddha, and Unani.")

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    # Start the chat session with an empty history
    st.session_state.chat_session = model.start_chat(history=[])

# Chat container
st.markdown("### 💬 Conversation")

# Display previous conversation messages with custom styling
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Input area at the bottom
st.markdown('<div class="input-container">', unsafe_allow_html=True)

prompt = st.text_input(
    "Ask your question about traditional medicine...",
    key="user_input",
    placeholder="e.g., What are the benefits of Ashwagandha in Ayurveda?",
    on_change=lambda: st.session_state.update({"submit": True}) if st.session_state.get("user_input") else None
)

st.markdown('</div>', unsafe_allow_html=True)

# Process input
if st.session_state.get("submit", False) and prompt:
    # Display user message in chat
    st.markdown(f'<div class="user-message">{prompt}</div>', unsafe_allow_html=True)
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Show typing indicator
    with st.spinner("Aushadi Veda is thinking..."):
        try:
            # Send the message to the model and get a response using retry function
            response = send_with_retry(st.session_state.chat_session, prompt)
            model_response = response.text

            # Display assistant response in chat
            st.markdown(f'<div class="assistant-message">{model_response}</div>', unsafe_allow_html=True)
            # Add assistant response to session state
            st.session_state.messages.append({"role": "assistant", "content": model_response})

            # Clear input and reset submit flag
            st.session_state.user_input = ""
            st.session_state.submit = False

        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.session_state.submit = False

    st.rerun()
