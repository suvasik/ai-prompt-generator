import streamlit as st
import google.generativeai as genai
import streamlit_antd_components as sac

# --- CONFIGURATION ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except:
    st.error("API Key missing! Please check Streamlit Secrets.")

st.set_page_config(page_title="Prompt Studio", page_icon="🪄", layout="wide")

# --- DARK CYBER UI CSS ---
st.markdown("""
    <style>
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* DARK BLUE GRADIENT BACKGROUND */
    .stApp {
        background: radial-gradient(circle at top right, #050b1a 0%, #00050d 100%);
        background-attachment: fixed;
    }

    /* SMALL PICTURES/TEXTURES IN BACKGROUND */
    .stApp::before {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: url("https://www.transparenttextures.com/patterns/circuit-board.png");
        opacity: 0.15;
        pointer-events: none;
    }

    /* MAIN GLASS CONTAINER */
    .main-box {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 40px;
        margin-top: 10px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.9);
    }

    /* VISIBLE BUTTONS (White with Dark Blue Text) */
    .stButton > button {
        width: auto !important;
        background: #ffffff !important; 
        color: #050b1a !important; 
        border: none !important;
        padding: 12px 35px !important;
        border-radius: 12px !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        box-shadow: 0 4px 20px rgba(255, 255, 255, 0.1) !important;
    }

    .stButton > button:hover {
        background: #00d2ff !important;
        color: white !important;
        transform: scale(1.03);
    }

    /* TEXT COLORS */
    h1, h2, h3, p, label { color: white !important; }

    .stTextArea textarea {
        background: rgba(0, 0, 0, 0.5) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE (Memory) ---
if "history" not in st.session_state: st.session_state.history = []
if "last_result" not in st.session_state: st.session_state.last_result = ""

# --- SIDEBAR MENU ---
with st.sidebar:
    st.markdown("<h1 style='color:white; font-size: 25px;'>🪄 Studio Menu</h1>", unsafe_allow_html=True)
    menu_item = sac.menu([
        sac.MenuItem('New Chat', icon='plus-square-fill'),
        sac.MenuItem('History', icon='clock-fill'),
        sac.MenuItem('Settings', icon='gear-wide-connected'),
    ], color='blue', variant='filled', index=0)

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# --- NAVIGATION LOGIC ---

if menu_item == 'New Chat':
    st.title("🚀 Prompt Generator")
    
    # If a prompt was generated, show the RESULT SCREEN
    if st.session_state.last_result:
        st.subheader("✨ Generated Result")
        st.code(st.session_state.last_result, language="text")
        
        # Left-aligned control buttons
        col1, col2, _ = st.columns([1, 1, 4])
        with col1:
            if st.button("🆕 New Chat"):
                st.session_state.last_result = "" # Clear result to go back to input box
                st.rerun()
        with col2:
            st.download_button("📥 Download", st.session_state.last_result, file_name="ai_prompt.txt")
            
    # If starting fresh, show the INPUT SCREEN
    else:
        user_input = st.text_area("What is your vision?", placeholder="A futuristic laboratory with bioluminescent plants...", height=150)
        if st.button("Generate Masterpiece"):
            if user_input:
                with st.spinner("AI 2.5 is processing..."):
                    try:
                        # USING GEMINI 2.5 FLASH AS REQUESTED
                        model = genai.GenerativeModel('gemini-2.5-flash') 
                        response = model.generate_content(f"Expand this into a professional AI prompt: {user_input}")
                        st.session_state.last_result = response.text
                        st.session_state.history.append({"input": user_input, "output": response.text})
                        st.rerun()
                    except Exception as e:
                        if "429" in str(e):
                            st.error("🚦 Rate Limit Reached. Please wait 1 minute and try again.")
                        else:
                            st.error(f"Error: {e}")

elif menu_item == 'History':
    st.title("📜 Neural Archive")
    if not st.session_state.history:
        st.info("No saved prompts yet.")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Prompt #{len(st.session_state.history)-i}"):
                st.write(f"**Idea:** {item['input']}")
                st.code(item['output'], language="text")

elif menu_item == 'Settings':
    st.title("⚙️ Config")
    st.slider("AI Temperature", 0.0, 1.0, 0.7)
    if st.button("🗑️ Clear Archive"):
        st.session_state.history = []
        st.session_state.last_result = ""
        st.success("History wiped.")
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
