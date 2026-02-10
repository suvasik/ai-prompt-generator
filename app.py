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

# --- 2. DARK UI CSS (Visible Buttons & Textures) ---
st.markdown("""
    <style>
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* DEEP NAVY BACKGROUND */
    .stApp {
        background: radial-gradient(circle at top right, #050b1a 0%, #00050d 100%);
        background-attachment: fixed;
    }

    /* AI TEXTURE OVERLAY */
    .stApp::before {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: url("https://www.transparenttextures.com/patterns/circuit-board.png");
        opacity: 0.12;
        pointer-events: none;
    }

    /* GLASS CONTAINER */
    .main-box {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 40px;
        margin-top: 10px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7);
    }

    /* VISIBLE BUTTONS (White with Deep Blue Text) */
    .stButton > button {
        width: auto !important;
        background-color: #ffffff !important; 
        color: #050b1a !important; 
        border: 2px solid #00d2ff !important;
        padding: 10px 30px !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important;
        visibility: visible !important;
        display: block !important;
    }

    .stButton > button:hover {
        background-color: #00d2ff !important;
        color: white !important;
        border: 2px solid white !important;
    }

    /* TEXT COLORS */
    h1, h2, h3, p, label { color: white !important; }

    /* INPUT FIELD */
    .stTextArea textarea {
        background: rgba(0, 0, 0, 0.3) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. STATE MANAGEMENT ---
if "history" not in st.session_state: st.session_state.history = []
if "last_result" not in st.session_state: st.session_state.last_result = ""

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>🪄 Studio</h2>", unsafe_allow_html=True)
    menu_item = sac.menu([
        sac.MenuItem('New Chat', icon='plus-square-fill'),
        sac.MenuItem('History', icon='clock-fill'),
        sac.MenuItem('Settings', icon='gear-wide-connected'),
    ], color='blue', variant='filled', index=0)

# Clear last_result if the sidebar 'New Chat' is explicitly clicked
if menu_item == 'New Chat' and st.sidebar.button("🔄 Reset View", use_container_width=True):
    st.session_state.last_result = ""
    st.rerun()

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# --- 5. LOGIC FLOW ---

if menu_item == 'New Chat':
    st.title("🚀 Prompt Generator")
    
    # Check if we should display the result
    if st.session_state.last_result:
        st.subheader("✨ Generated Masterpiece")
        st.code(st.session_state.last_result, language="text")
        
        # Row for working buttons
        col1, col2, _ = st.columns([1, 1, 4])
        with col1:
            if st.button("🆕 New Chat"):
                st.session_state.last_result = ""
                st.rerun()
        with col2:
            st.download_button("📥 Download", st.session_state.last_result, file_name="ai_prompt.txt")
            
    else:
        # Input Screen
        user_input = st.text_area("What is your vision?", placeholder="A futuristic city with bioluminescent neon lights...", height=150)
        if st.button("GENERATE PROMPT"):
            if user_input:
                with st.spinner("Gemini 2.5 is processing..."):
                    try:
                        # USING 2.5 VERSION
                        model = genai.GenerativeModel('gemini-2.5-flash') 
                        response = model.generate_content(f"Expand this into a professional AI prompt: {user_input}")
                        st.session_state.last_result = response.text
                        st.session_state.history.append({"input": user_input, "output": response.text})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Please enter some text first.")

elif menu_item == 'History':
    st.title("📜 Neural Archive")
    if not st.session_state.history:
        st.info("Your archive is empty.")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Prompt #{len(st.session_state.history)-i}"):
                st.write(f"**Input:** {item['input']}")
                st.code(item['output'], language="text")

elif menu_item == 'Settings':
    st.title("⚙️ Config")
    st.slider("AI Creativity", 0.0, 1.0, 0.7)
    if st.button("🗑️ Clear Archive"):
        st.session_state.history = []
        st.session_state.last_result = ""
        st.success("History wiped.")
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
