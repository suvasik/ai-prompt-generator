import streamlit as st
import google.generativeai as genai
import streamlit_antd_components as sac  # Updated this line

# --- 1. CONFIGURATION ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except:
    st.error("API Key not found in Secrets!")

st.set_page_config(page_title="Prompt Studio", page_icon="🪄", layout="wide")

# --- 2. THEME & UI ---
st.markdown("""
    <style>
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .main {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url("https://images.unsplash.com/photo-1614850523296-d8c1af93d400?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session States
if "history" not in st.session_state:
    st.session_state.history = []
if "generated_prompt" not in st.session_state:
    st.session_state.generated_prompt = ""

# --- 3. SIDEBAR MENU ---
with st.sidebar:
    st.title("🪄 AI Menu")
    
    # Using the Ant Design Menu for a professional look
    menu_item = sac.menu([
        sac.MenuItem('New Chat', icon='plus-circle-fill'),
        sac.MenuItem('History', icon='clock-history'),
        sac.MenuItem('Settings', icon='gear-fill'),
    ], format_func='title', open_all=True)

# --- 4. APP LOGIC ---

# NEW CHAT PAGE
if menu_item == 'New Chat':
    st.title("✨ Create an Enhanced Prompt")
    
    user_input = st.text_area("What is your basic idea?", placeholder="e.g. A cat drinking tea in space", height=100)
    
    if st.button("Generate Masterpiece"):
        if user_input:
            with st.spinner("AI is thinking..."):
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(f"Act as a Prompt Engineer. Expand this into a high-quality AI prompt: {user_input}")
                    st.session_state.generated_prompt = response.text
                    
                    # Store in history
                    st.session_state.history.append({"input": user_input, "output": response.text})
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a sentence first.")

    if st.session_state.generated_prompt:
        st.subheader("Enhanced Result:")
        st.info(st.session_state.generated_prompt)
        if st.button("Clear Result"):
            st.session_state.generated_prompt = ""
            st.rerun()

# HISTORY PAGE
elif menu_item == 'History':
    st.title("📜 Past Prompts")
    if not st.session_state.history:
        st.write("No history found.")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Prompt {len(st.session_state.history)-i}: {item['input'][:40]}..."):
                st.write(f"**Your Input:** {item['input']}")
                st.write("**AI Enhanced:**")
                st.code(item['output'])
        
        if st.button("Clear All History"):
            st.session_state.history = []
            st.rerun()

# SETTINGS PAGE
elif menu_item == 'Settings':
    st.title("⚙️ App Settings")
    st.selectbox("AI Model Version", ["Gemini 2.5 Flash (Fast)", "Gemini 3 Pro (Smart)"])
    st.slider("Creativity Level", 0.0, 1.0, 0.7)
    st.write("Current API Status: ✅ Active")
