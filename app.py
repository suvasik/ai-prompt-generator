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

# --- CSS FOR YOUR CUSTOM BLUE GRADIENT BACKGROUND ---
st.markdown(f"""
    <style>
    .stDeployButton {{display:none;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* THE BACKGROUND IMAGE SETTING */
    .stApp {{
        background: linear-gradient(rgba(0, 0, 50, 0.5), rgba(0, 0, 50, 0.5)), 
                    url("REPLACE_WITH_YOUR_IMAGE_LINK_HERE");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* Main Box Styling */
    .main-box {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        margin-top: 20px;
    }}

    /* Left-aligned Button Design */
    .stButton > button {{
        width: auto !important;
        background: linear-gradient(90deg, #00d2ff, #3a7bd5) !important;
        color: white !important;
        border: none !important;
        padding: 10px 25px !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }}
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "history" not in st.session_state: st.session_state.history = []
if "last_result" not in st.session_state: st.session_state.last_result = ""

# --- SIDEBAR MENU ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>🪄 Navigation</h2>", unsafe_allow_html=True)
    menu_item = sac.menu([
        sac.MenuItem('New Chat', icon='chat-left-dots-fill'),
        sac.MenuItem('History', icon='clock-history'),
        sac.MenuItem('Settings', icon='gear-fill'),
    ], color='blue', variant='filled')

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# --- NEW CHAT LOGIC ---
if menu_item == 'New Chat':
    st.title("🚀 AI Prompt Generator")
    
    if st.session_state.last_result:
        st.subheader("✨ Enhanced Result")
        # Native Streamlit code block provides the 'Copy' button in the top right
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
        user_input = st.text_area("What is your idea?", placeholder="Type your base prompt here...", height=120)
        if st.button("Generate Masterpiece"):
            if user_input:
                with st.spinner("AI is crafting your prompt..."):
                    try:
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        response = model.generate_content(f"Expand this into a detailed AI prompt: {user_input}")
                        st.session_state.last_result = response.text
                        st.session_state.history.append({"input": user_input, "output": response.text})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

# --- HISTORY LOGIC ---
elif menu_item == 'History':
    st.title("📜 Chat History")
    if not st.session_state.history:
        st.info("No saved prompts yet.")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Prompt #{len(st.session_state.history)-i}"):
                st.write(f"**Input:** {item['input']}")
                st.code(item['output'], language="text")

# --- SETTINGS LOGIC ---
elif menu_item == 'Settings':
    st.title("⚙️ Settings")
    st.slider("AI Creativity", 0.0, 1.0, 0.7)
    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        st.success("History deleted!")

st.markdown('</div>', unsafe_allow_html=True)
