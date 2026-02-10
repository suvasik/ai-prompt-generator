import streamlit as st
import google.generativeai as genai
import streamlit_antd_components as sac

# --- 1. CONFIGURATION ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except:
    st.error("API Key missing! Please check Streamlit Secrets.")

st.set_page_config(page_title="Prompt Studio", page_icon="🪄", layout="wide")

# --- 2. THE "TOP NAV & NEON" CSS ---
st.markdown("""
    <style>
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* DEEP NAVY BACKGROUND */
    .stApp {
        background: radial-gradient(circle at top right, #050b1a 0%, #00050d 100%) !important;
        background-attachment: fixed;
    }

    /* TEXTURE OVERLAY */
    .stApp::before {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: url("https://www.transparenttextures.com/patterns/circuit-board.png");
        opacity: 0.1;
        pointer-events: none;
        z-index: 0;
    }

    /* MAIN CONTAINER */
    .main-box {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        position: relative;
        z-index: 1;
        margin-top: 20px;
    }

    /* TOP NAVIGATION STYLING */
    .nav-container {
        background: rgba(0, 0, 0, 0.5);
        padding: 10px;
        border-radius: 15px;
        margin-bottom: 20px;
    }

    /* NEON CYAN BUTTONS */
    div.stButton > button {
        background-color: #00f2fe !important;
        color: #050b1a !important;
        border: 2px solid #ffffff !important;
        padding: 12px 35px !important;
        border-radius: 10px !important;
        font-size: 16px !important;
        font-weight: 900 !important;
        box-shadow: 0px 0px 15px rgba(0, 242, 254, 0.5) !important;
        visibility: visible !important;
        z-index: 999 !important;
    }

    div.stButton > button:hover {
        background-color: #ffffff !important;
        box-shadow: 0px 0px 25px rgba(255, 255, 255, 0.8) !important;
        transform: scale(1.02);
    }

    /* TEXT COLORS */
    h1, h2, h3, p, label, span {
        color: #ffffff !important;
    }

    /* INPUT AREA */
    .stTextArea textarea {
        background: rgba(0, 0, 0, 0.5) !important;
        color: white !important;
        border: 1px solid #00f2fe !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "history" not in st.session_state: st.session_state.history = []
if "last_result" not in st.session_state: st.session_state.last_result = ""

# --- 4. TOP NAVIGATION BAR ---
# This replaces the sidebar menu
menu_item = sac.tabs([
    sac.TabsItem(label='New Chat', icon='chat-left-dots-fill'),
    sac.TabsItem(label='History', icon='clock-history'),
    sac.TabsItem(label='Settings', icon='gear-fill'),
], align='center', variant='toggle', color='cyan', index=0)

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# --- 5. PAGE LOGIC ---
if menu_item == 'New Chat':
    st.title("🚀 Prompt Generator")
    
    if st.session_state.last_result:
        st.subheader("✨ Enhanced Result")
        st.code(st.session_state.last_result, language="text")
        
        col1, col2, _ = st.columns([1, 1, 4])
        with col1:
            if st.button("🆕 New Chat"):
                st.session_state.last_result = ""
                st.rerun()
        with col2:
            st.download_button("📥 Download", st.session_state.last_result, file_name="ai_prompt.txt")
            
    else:
        user_input = st.text_area("Your Idea:", placeholder="Describe your vision...", height=150)
        if st.button("GENERATE MASTERPIECE"):
            if user_input:
                with st.spinner("AI 2.5 Processing..."):
                    try:
                        # KEEPING GEMINI 2.5 FLASH
                        model = genai.GenerativeModel('gemini-2.5-flash') 
                        response = model.generate_content(f"Expand into a pro prompt: {user_input}")
                        st.session_state.last_result = response.text
                        st.session_state.history.append({"input": user_input, "output": response.text})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

elif menu_item == 'History':
    st.title("📜 Archive")
    if not st.session_state.history:
        st.info("No records yet. Go to 'New Chat' to start.")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Prompt #{len(st.session_state.history)-i}"):
                st.write(f"**Input:** {item['input']}")
                st.code(item['output'], language="text")

elif menu_item == 'Settings':
    st.title("⚙️ System Settings")
    st.write("Model: **Gemini 2.5 Flash**")
    if st.button("🗑️ Reset All Data"):
        st.session_state.history = []
        st.session_state.last_result = ""
        st.success("Cleared!")
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
