import streamlit as st
import google.generativeai as genai
import streamlit_antd_components as sac

# --- CONFIGURATION ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except:
    st.error("API Key missing! Please add GEMINI_KEY to Streamlit Secrets.")

st.set_page_config(page_title="Prompt Studio", page_icon="🪄", layout="wide")

# --- CYBER UI CSS ---
st.markdown("""
    <style>
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stApp {
        background: linear-gradient(rgba(10, 10, 35, 0.9), rgba(10, 10, 35, 0.9)), 
                    url("https://images.unsplash.com/photo-1639322537228-f710d846310a?q=80&w=2000&auto=format&fit=crop");
        background-size: cover;
    }
    .main-box {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
    }
    .stButton > button {
        width: auto !important;
        background: linear-gradient(90deg, #6c5ce7, #00d2ff) !important;
        color: white !important;
        border: none !important;
        padding: 10px 20px !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "history" not in st.session_state: st.session_state.history = []
if "last_result" not in st.session_state: st.session_state.last_result = ""

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("# 🪄 Menu")
    menu_item = sac.menu([
        sac.MenuItem('New Chat', icon='plus-circle'),
        sac.MenuItem('History', icon='clock-history'),
        sac.MenuItem('Settings', icon='sliders'),
    ], color='indigo', variant='filled')

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# --- LOGIC: NEW CHAT ---
if menu_item == 'New Chat':
    st.title("🚀 AI Prompt Generator")
    
    # If a result exists, show the result screen
    if st.session_state.last_result:
        st.subheader("✨ Your Enhanced Prompt")
        st.code(st.session_state.last_result, language="text")
        
        # Left-aligned action buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("🆕 Start New Chat"):
                st.session_state.last_result = "" # This clears the current screen
                st.rerun()
        with col2:
            st.download_button("📥 Download", st.session_state.last_result, file_name="prompt.txt")
            
    # If no result exists, show the input screen
    else:
        user_input = st.text_area("What is your idea?", placeholder="Describe your vision...", height=150)
        if st.button("Generate Masterpiece"):
            if user_input:
                with st.spinner("Processing..."):
                    try:
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        response = model.generate_content(f"Expand this into a professional AI prompt: {user_input}")
                        st.session_state.last_result = response.text
                        st.session_state.history.append({"input": user_input, "output": response.text})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

# --- LOGIC: HISTORY ---
elif menu_item == 'History':
    st.title("📜 Neural Archive")
    if not st.session_state.history:
        st.info("No history yet.")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Prompt #{len(st.session_state.history)-i}"):
                st.write(f"**Input:** {item['input']}")
                st.code(item['output'], language="text")

# --- LOGIC: SETTINGS ---
elif menu_item == 'Settings':
    st.title("⚙️ Config")
    st.slider("Creativity", 0.0, 1.0, 0.7)
    st.info("System optimized for Gemini 2.5 Flash.")

st.markdown('</div>', unsafe_allow_html=True)
