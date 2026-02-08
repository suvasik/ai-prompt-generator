import streamlit as st
import google.generativeai as genai
import streamlit_antd_components as sac

# Try to import copy tool, but don't crash if it fails
try:
    from st_copy_to_clipboard import copy_to_clipboard
    HAS_COPY = True
except ImportError:
    HAS_COPY = False

# --- CONFIGURATION ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except Exception:
    st.error("API Key missing! Add GEMINI_KEY to Streamlit Secrets.")

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
    /* Left-aligning buttons */
    .stButton > button {
        width: auto !important;
        background: linear-gradient(90deg, #6c5ce7, #00d2ff) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

if "history" not in st.session_state: st.session_state.history = []
if "last_result" not in st.session_state: st.session_state.last_result = ""

# --- SIDEBAR (Left Side) ---
with st.sidebar:
    st.markdown("# 🪄 Menu")
    menu_item = sac.menu([
        sac.MenuItem('New Chat', icon='plus-circle'),
        sac.MenuItem('History', icon='clock-history'),
        sac.MenuItem('Settings', icon='sliders'),
    ], color='indigo', variant='filled')

# --- MAIN PAGE ---
st.markdown('<div class="main-box">', unsafe_allow_html=True)

if menu_item == 'New Chat':
    st.title("🚀 AI Prompt Generator")
    user_input = st.text_area("Enter idea:", placeholder="A futuristic city...", height=100)
    
    if st.button("Generate"):
        if user_input:
            with st.spinner("Processing..."):
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(f"Expand this into a high-quality prompt: {user_input}")
                st.session_state.last_result = response.text
                st.session_state.history.append({"input": user_input, "output": response.text})

    if st.session_state.last_result:
        st.subheader("Enhanced Result")
        st.info(st.session_state.last_result)
        
        # Action Buttons (Left Aligned)
        col1, col2, _ = st.columns([1, 1, 4])
        with col1:
            if HAS_COPY:
                copy_to_clipboard(st.session_state.last_result)
                st.caption("Click to Copy")
            else:
                st.warning("Copy tool not installed")
        with col2:
            st.download_button("📥 Download", st.session_state.last_result, file_name="prompt.txt")

elif menu_item == 'History':
    st.title("📜 History")
    for i, item in enumerate(reversed(st.session_state.history)):
        with st.expander(f"Prompt {len(st.session_state.history)-i}"):
            st.write(f"**Input:** {item['input']}")
            st.code(item['output'])

elif menu_item == 'Settings':
    st.title("⚙️ Settings")
    st.write("App is running in Cyber-Mode.")
    st.slider("Creativity Level", 0.0, 1.0, 0.7)

st.markdown('</div>', unsafe_allow_html=True)
