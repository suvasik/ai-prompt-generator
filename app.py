import streamlit as st
import google.generativeai as genai
import streamlit_antd_components as sac

# --- 1. CONFIGURATION ---
try:
    # Ensure your secret key is named exactly GEMINI_KEY in Streamlit Cloud
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error("API Key Error: Please check your Streamlit Secrets.")

st.set_page_config(page_title="Prompt Studio", page_icon="🪄", layout="wide")

# --- 2. CSS FOR VISIBILITY & LAYOUT ---
st.markdown("""
    <style>
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* BACKGROUND */
    .stApp {
        background: radial-gradient(circle at top right, #4facfe 0%, #00f2fe 20%, #0061ff 100%);
        background-attachment: fixed;
    }

    /* MAIN CONTAINER */
    .main-box {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(15px);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 40px;
        margin-top: 10px;
    }

    /* ALL BUTTONS - HIGH VISIBILITY */
    .stButton > button {
        width: auto !important;
        background-color: #ffffff !important; 
        color: #0061ff !important; 
        border: 2px solid #00d2ff !important;
        padding: 10px 25px !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
        text-transform: uppercase;
    }

    .stButton > button:hover {
        background-color: #00d2ff !important;
        color: white !important;
        border: 2px solid #ffffff !important;
    }

    /* TEXT BOX STYLING */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid white !important;
        font-size: 16px !important;
    }

    /* HEADERS */
    h1, h2, h3 { color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE INITIALIZATION ---
# This acts as the "Memory" of your app
if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = ""

# --- 4. SIDEBAR MENU ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>🪄 Studio Menu</h2>", unsafe_allow_html=True)
    # This menu controls what page is visible
    menu_item = sac.menu([
        sac.MenuItem('New Chat', icon='plus-square-fill'),
        sac.MenuItem('History', icon='clock-fill'),
        sac.MenuItem('Settings', icon='gear-wide-connected'),
    ], color='blue', variant='filled', index=0)

# Main container start
st.markdown('<div class="main-box">', unsafe_allow_html=True)

# --- 5. PAGE LOGIC ---

# PAGE: NEW CHAT
if menu_item == 'New Chat':
    st.title("🚀 AI Prompt Generator")
    
    # If a result already exists, show the result view
    if st.session_state.last_result:
        st.markdown("### ✨ Your Enhanced Prompt")
        st.code(st.session_state.last_result, language="text")
        
        # Action row (Left Aligned)
        col1, col2, _ = st.columns([1, 1, 4])
        with col1:
            if st.button("🆕 Start New"):
                st.session_state.last_result = "" # Clear result
                st.rerun() # Refresh to show input box
        with col2:
            st.download_button(
                label="📥 Download",
                data=st.session_state.last_result,
                file_name="prompt.txt",
                mime="text/plain"
            )
            
    # If no result exists, show the input view
    else:
        user_input = st.text_area("What is your basic idea?", placeholder="e.g. A futuristic city in the clouds...", height=150)
        if st.button("GENERATE MASTERPIECE"):
            if user_input:
                with st.spinner("Neural Processing..."):
                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        response = model.generate_content(f"Expand this into a professional prompt: {user_input}")
                        st.session_state.last_result = response.text
                        st.session_state.history.append({"input": user_input, "output": response.text})
                        st.rerun() # Refresh to show the result view
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Please enter some text first.")

# PAGE: HISTORY
elif menu_item == 'History':
    st.title("📜 Neural Archive")
    if not st.session_state.history:
        st.info("No saved prompts yet. Generate something in 'New Chat'!")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Prompt #{len(st.session_state.history)-i}"):
                st.markdown(f"**Input:** {item['input']}")
                st.code(item['output'], language="text")

# PAGE: SETTINGS
elif menu_item == 'Settings':
    st.title("⚙️ System Config")
    st.slider("AI Creativity (Temperature)", 0.0, 1.0, 0.7)
    
    st.markdown("---")
    if st.button("🗑️ Reset All History"):
        st.session_state.history = []
        st.session_state.last_result = ""
        st.success("All data cleared.")
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
