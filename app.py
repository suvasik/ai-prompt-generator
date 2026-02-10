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

# --- CSS FOR SOFT BLUE GRADIENT & TEXTURES ---
st.markdown("""
    <style>
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* LIGHT BLUE TEXTURED GRADIENT BACKGROUND */
    .stApp {
        background: radial-gradient(circle at top right, #4facfe 0%, #00f2fe 20%, #0061ff 100%);
        background-attachment: fixed;
    }

    /* Adding a light pattern overlay to mimic the textures */
    .stApp::before {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: url("https://www.transparenttextures.com/patterns/cubes.png");
        opacity: 0.15;
        pointer-events: none;
    }

    /* Main Container with Soft Glass Effect */
    .main-box {
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 40px;
        margin-top: 10px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 50, 0.3);
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: rgba(0, 50, 100, 0.8) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Left-Aligned Buttons */
    .stButton > button {
        width: auto !important;
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%) !important;
        color: white !important;
        border: none !important;
        padding: 10px 30px !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: 0.4s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important;
    }
    
    /* Text Color Fixes */
    h1, h2, h3, p, label {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "history" not in st.session_state: st.session_state.history = []
if "last_result" not in st.session_state: st.session_state.last_result = ""

# --- SIDEBAR (Left Menu) ---
with st.sidebar:
    st.markdown("<h1 style='color:white; font-size: 25px;'>🪄 Studio Menu</h1>", unsafe_allow_html=True)
    menu_item = sac.menu([
        sac.MenuItem('New Chat', icon='plus-square-fill'),
        sac.MenuItem('History', icon='clock-fill'),
        sac.MenuItem('Settings', icon='gear-wide-connected'),
    ], color='blue', variant='filled')

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# --- NAVIGATION LOGIC ---
if menu_item == 'New Chat':
    st.title("🚀 Prompt Generator")
    
    if st.session_state.last_result:
        st.subheader("✨ Result")
        st.code(st.session_state.last_result, language="text")
        
        # Action Buttons (Left Aligned)
        col1, col2, _ = st.columns([1, 1, 4])
        with col1:
            if st.button("🆕 New Chat"):
                st.session_state.last_result = ""
                st.rerun()
        with col2:
            st.download_button("📥 Download", st.session_state.last_result, file_name="ai_prompt.txt")
            
    else:
        user_input = st.text_area("What's on your mind?", placeholder="e.g. A futuristic ocean city...", height=150)
        if st.button("Generate"):
            if user_input:
                with st.spinner("AI is thinking..."):
                    try:
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        response = model.generate_content(f"Expand this into a professional prompt: {user_input}")
                        st.session_state.last_result = response.text
                        st.session_state.history.append({"input": user_input, "output": response.text})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

elif menu_item == 'History':
    st.title("📜 Archive")
    if not st.session_state.history:
        st.write("No history recorded.")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Prompt #{len(st.session_state.history)-i}"):
                st.write(f"**Input:** {item['input']}")
                st.code(item['output'], language="text")

elif menu_item == 'Settings':
    st.title("⚙️ System")
    st.slider("AI Temperature", 0.0, 1.0, 0.7)
    if st.button("🗑️ Reset Archive"):
        st.session_state.history = []
        st.success("History Cleared!")

st.markdown('</div>', unsafe_allow_html=True)
