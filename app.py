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

# --- CUSTOM CSS (Blue AI Gradient + Glassmorphism) ---
st.markdown("""
    <style>
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Background Image with Blue Gradient & AI Icons */
    .stApp {
        background: linear-gradient(rgba(10, 10, 45, 0.7), rgba(10, 10, 45, 0.7)), 
                    url("https://img.freepik.com/free-vector/digital-technology-background-with-abstract-geometric-shapes_1017-38917.jpg");
        background-size: cover;
        background-attachment: fixed;
    }

    /* Main Glass Container */
    .main-box {
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 25px;
        padding: 40px;
        margin-top: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    /* Button Styling */
    .stButton > button {
        width: auto !important;
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%) !important;
        color: white !important;
        border: none !important;
        padding: 12px 24px !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        transition: 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(0, 210, 255, 0.5) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "history" not in st.session_state: st.session_state.history = []
if "last_result" not in st.session_state: st.session_state.last_result = ""

# --- SIDEBAR (Left Menu) ---
with st.sidebar:
    st.markdown("<h1 style='color:white;'>🪄 Studio</h1>", unsafe_allow_html=True)
    menu_item = sac.menu([
        sac.MenuItem('New Chat', icon='plus-circle-fill'),
        sac.MenuItem('History', icon='clock-history'),
        sac.MenuItem('Settings', icon='gear-wide-connected'),
    ], color='blue', variant='filled')

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# --- LOGIC: NEW CHAT ---
if menu_item == 'New Chat':
    st.markdown("<h1 style='color:white;'>🚀 AI Prompt Generator</h1>", unsafe_allow_html=True)
    
    # OUTPUT SCREEN
    if st.session_state.last_result:
        st.markdown("<h3 style='color:#00d2ff;'>✨ Enhanced Result</h3>", unsafe_allow_html=True)
        # Built-in Copy functionality
        st.code(st.session_state.last_result, language="text")
        
        # Left-aligned action buttons
        col1, col2, _ = st.columns([1.2, 1.2, 4])
        with col1:
            if st.button("🆕 Start New Chat"):
                st.session_state.last_result = ""
                st.rerun()
        with col2:
            st.download_button("📥 Download .txt", st.session_state.last_result, file_name="prompt.txt")
            
    # INPUT SCREEN
    else:
        user_input = st.text_area("What's your vision?", placeholder="A futuristic laboratory with holographic displays...", height=150)
        if st.button("Generate Masterpiece"):
            if user_input:
                with st.spinner("Decoding your thoughts..."):
                    try:
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        response = model.generate_content(f"Expand this into a professional prompt: {user_input}")
                        st.session_state.last_result = response.text
                        st.session_state.history.append({"input": user_input, "output": response.text})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Neural Error: {e}")

# --- LOGIC: HISTORY ---
elif menu_item == 'History':
    st.markdown("<h1 style='color:white;'>📜 Neural Archive</h1>", unsafe_allow_html=True)
    if not st.session_state.history:
        st.info("The archive is empty.")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Prompt #{len(st.session_state.history)-i}"):
                st.write(f"**Request:** {item['input']}")
                st.code(item['output'], language="text")

# --- LOGIC: SETTINGS ---
elif menu_item == 'Settings':
    st.markdown("<h1 style='color:white;'>⚙️ System Config</h1>", unsafe_allow_html=True)
    st.slider("Model Temperature (Creativity)", 0.0, 1.0, 0.7)
    if st.button("🗑️ Clear All History"):
        st.session_state.history = []
        st.success("Archive Cleared!")

st.markdown('</div>', unsafe_allow_html=True)
