import streamlit as st
import google.generativeai as genai
import streamlit_antd_components as sac

# --- 1. API CONFIGURATION ---
try:
    # Ensure your Secret Key in Streamlit Cloud is named GEMINI_KEY
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except Exception:
    st.error("🔑 API Key Missing: Please add 'GEMINI_KEY' to your Streamlit Secrets.")

st.set_page_config(page_title="Prompt Studio", page_icon="🪄", layout="wide")

# --- 2. CUSTOM UI STYLING (Blue Textured Gradient) ---
st.markdown("""
    <style>
    /* Clean up default Streamlit elements */
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* BACKGROUND: Blue Gradient with Light Texture */
    .stApp {
        background: radial-gradient(circle at top right, #4facfe 0%, #00f2fe 20%, #0061ff 100%);
        background-attachment: fixed;
    }
    .stApp::before {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: url("https://www.transparenttextures.com/patterns/cubes.png");
        opacity: 0.12;
        pointer-events: none;
    }

    /* GLASS CONTAINER */
    .main-box {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 2px solid rgba(255, 255, 255, 0.25);
        border-radius: 20px;
        padding: 40px;
        margin-top: 10px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 50, 0.3);
    }

    /* BUTTONS: Solid white for high visibility on blue background */
    .stButton > button {
        width: auto !important;
        background-color: #ffffff !important; 
        color: #0061ff !important; 
        border: 2px solid #00d2ff !important;
        padding: 12px 28px !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
        transition: 0.3s ease all;
    }

    .stButton > button:hover {
        background-color: #00d2ff !important;
        color: white !important;
        transform: translateY(-2px);
    }

    /* TEXT COLOR FIXES */
    h1, h2, h3, p, label, .stMarkdown {
        color: white !important;
    }

    /* INPUT TEXT AREA */
    .stTextArea textarea {
        background: rgba(0, 0, 0, 0.2) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. STATE MANAGEMENT ---
if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = ""

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>🪄 Neural Studio</h2>", unsafe_allow_html=True)
    menu_item = sac.menu([
        sac.MenuItem('New Chat', icon='plus-square-fill'),
        sac.MenuItem('History', icon='clock-fill'),
        sac.MenuItem('Settings', icon='gear-wide-connected'),
    ], color='blue', variant='filled', index=0)

# Wrap everything in our Glass Box
st.markdown('<div class="main-box">', unsafe_allow_html=True)

# --- 5. APP LOGIC ---

# PAGE: NEW CHAT
if menu_item == 'New Chat':
    st.title("🚀 Prompt Generator")
    
    # OUTPUT SCREEN
    if st.session_state.last_result:
        st.markdown("### ✨ Enhanced AI Prompt")
        st.code(st.session_state.last_result, language="text")
        
        # Action Buttons (Left Aligned)
        col1, col2, _ = st.columns([1, 1, 4])
        with col1:
            if st.button("🆕 Start New"):
                st.session_state.last_result = ""
                st.rerun()
        with col2:
            st.download_button(
                label="📥 Download",
                data=st.session_state.last_result,
                file_name="enhanced_prompt.txt",
                mime="text/plain"
            )
            
    # INPUT SCREEN
    else:
        user_input = st.text_area("What is your basic idea?", placeholder="e.g. A cyberpunk samurai in a rainy neon city...", height=150)
        if st.button("GENERATE MASTERPIECE"):
            if user_input:
                with st.spinner("Decoding your vision..."):
                    try:
                        # Using Gemini 2.0 Flash
                        model = genai.GenerativeModel('gemini-2.0-flash') 
                        response = model.generate_content(f"Act as a professional Prompt Engineer. Expand this idea into a high-quality AI image generation prompt: {user_input}")
                        
                        st.session_state.last_result = response.text
                        st.session_state.history.append({"input": user_input, "output": response.text})
                        st.rerun() 
                    except Exception as e:
                        if "429" in str(e):
                            st.error("🚦 Quota Reached! Please wait 60 seconds. Google's Free Tier limits how many prompts you can make per minute.")
                        else:
                            st.error(f"⚠️ Model Error: {e}")
            else:
                st.warning("Please type an idea first!")

# PAGE: HISTORY
elif menu_item == 'History':
    st.title("📜 Archive")
    if not st.session_state.history:
        st.info("No prompts saved yet. Start a New Chat to begin!")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Prompt #{len(st.session_state.history)-i}"):
                st.write(f"**Original Idea:** {item['input']}")
                st.code(item['output'], language="text")

# PAGE: SETTINGS
elif menu_item == 'Settings':
    st.title("⚙️ System Config")
    st.write("Current Model: **Gemini 2.0 Flash**")
    st.slider("Creativity (Temperature)", 0.0, 1.0, 0.7)
    
    st.markdown("---")
    if st.button("🗑️ Wipe All App Data"):
        st.session_state.history = []
        st.session_state.last_result = ""
        st.success("All history and current sessions cleared.")
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
