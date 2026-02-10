import streamlit as st
import google.generativeai as genai
import streamlit_antd_components as sac

# --- 1. CONFIGURATION ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except Exception:
    st.error("API Key Error: Please check your Streamlit Secrets.")

st.set_page_config(page_title="Prompt Studio", page_icon="🪄", layout="wide")

# --- 2. CSS FOR VISIBILITY ---
st.markdown("""
    <style>
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        background: radial-gradient(circle at top right, #4facfe 0%, #00f2fe 20%, #0061ff 100%);
        background-attachment: fixed;
    }

    .main-box {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(15px);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 40px;
        margin-top: 10px;
    }

    .stButton > button {
        width: auto !important;
        background-color: #ffffff !important; 
        color: #0061ff !important; 
        border: 2px solid #00d2ff !important;
        padding: 10px 25px !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    }

    .stButton > button:hover {
        background-color: #00d2ff !important;
        color: white !important;
    }

    h1, h2, h3 { color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = ""

# --- 4. SIDEBAR MENU ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>🪄 Studio Menu</h2>", unsafe_allow_html=True)
    menu_item = sac.menu([
        sac.MenuItem('New Chat', icon='plus-square-fill'),
        sac.MenuItem('History', icon='clock-fill'),
        sac.MenuItem('Settings', icon='gear-wide-connected'),
    ], color='blue', variant='filled', index=0)

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# --- 5. PAGE LOGIC ---
if menu_item == 'New Chat':
    st.title("🚀 AI Prompt Generator")
    
    if st.session_state.last_result:
        st.markdown("### ✨ Your Enhanced Prompt")
        st.code(st.session_state.last_result, language="text")
        
        col1, col2, _ = st.columns([1, 1, 4])
        with col1:
            if st.button("🆕 Start New"):
                st.session_state.last_result = "" 
                st.rerun()
        with col2:
            st.download_button(label="📥 Download", data=st.session_state.last_result, file_name="prompt.txt")
            
    else:
        user_input = st.text_area("What is your basic idea?", placeholder="e.g. A futuristic city...", height=150)
        if st.button("GENERATE MASTERPIECE"):
            if user_input:
                with st.spinner("Neural Processing..."):
                    try:
                        # FIXED MODEL NAME HERE
                        model = genai.GenerativeModel('gemini-1.5-flash-latest') 
                        response = model.generate_content(f"Expand this into a professional prompt: {user_input}")
                        st.session_state.last_result = response.text
                        st.session_state.history.append({"input": user_input, "output": response.text})
                        st.rerun() 
                    except Exception as e:
                        st.error(f"Model Error: {e}")
            else:
                st.warning("Please enter some text.")

elif menu_item == 'History':
    st.title("📜 Neural Archive")
    if not st.session_state.history:
        st.info("No saved prompts yet.")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Prompt #{len(st.session_state.history)-i}"):
                st.markdown(f"**Input:** {item['input']}")
                st.code(item['output'], language="text")

elif menu_item == 'Settings':
    st.title("⚙️ Config")
    st.slider("AI Creativity", 0.0, 1.0, 0.7)
    if st.button("🗑️ Reset All History"):
        st.session_state.history = []
        st.session_state.last_result = ""
        st.success("Cleared.")
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
