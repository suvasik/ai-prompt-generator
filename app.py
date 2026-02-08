import streamlit as st
import google.generativeai as genai
import streamlit_antd_components as sac
from st_copy_to_clipboard import copy_to_clipboard

# --- CONFIGURATION ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except:
    st.error("API Key not found in Secrets! Please check Streamlit Cloud Secrets.")

st.set_page_config(page_title="Prompt Studio", page_icon="🪄", layout="wide")

# --- CUSTOM CSS (Left Aligned & Glassmorphism) ---
st.markdown("""
    <style>
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    
    /* Background */
    .stApp {
        background: linear-gradient(rgba(10, 10, 35, 0.9), rgba(10, 10, 35, 0.9)), 
                    url("https://images.unsplash.com/photo-1639322537228-f710d846310a?q=80&w=2000&auto=format&fit=crop");
        background-size: cover;
    }

    /* Main Container */
    .main-box {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        color: white;
    }

    /* Left Aligning Button Containers */
    .stButton > button {
        width: auto !important; /* Prevents buttons from stretching full width */
        padding: 10px 25px !important;
        background: linear-gradient(90deg, #6c5ce7, #00d2ff) !important;
        border: none !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
    }

    /* Style for the generated output */
    .output-text {
        background: rgba(0, 0, 0, 0.5);
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #00d2ff;
        margin-bottom: 15px;
        font-family: 'Courier New', monospace;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State
if "history" not in st.session_state: st.session_state.history = []
if "last_result" not in st.session_state: st.session_state.last_result = ""

# --- SIDEBAR MENU (LEFT SIDE) ---
with st.sidebar:
    st.markdown("## 🪄 Neural Menu")
    menu_item = sac.menu([
        sac.MenuItem('New Chat', icon='plus-circle'),
        sac.MenuItem('History', icon='clock-history'),
        sac.MenuItem('Settings', icon='sliders2-vertical'),
    ], color='indigo', variant='filled')
    
    st.divider()
    if st.button("🗑️ Clear App Data"):
        st.session_state.history = []
        st.session_state.last_result = ""
        st.rerun()

# --- MAIN PAGE CONTENT ---
st.markdown('<div class="main-box">', unsafe_allow_html=True)

if menu_item == 'New Chat':
    st.title("🚀 AI Prompt Generator")
    
    user_input = st.text_area("Enter your basic idea:", placeholder="e.g. A futuristic city underwater", height=100)
    
    # Generate Button (Left Aligned)
    if st.button("Generate Enhanced Text"):
        if user_input:
            with st.spinner("Neural Processing..."):
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(f"Act as a professional Prompt Engineer. Expand this: {user_input}")
                    st.session_state.last_result = response.text
                    st.session_state.history.append({"input": user_input, "output": response.text})
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Input required.")

    # Results Section
    if st.session_state.last_result:
        st.markdown("### ⚡ Enhanced Result")
        st.markdown(f'<div class="output-text">{st.session_state.last_result}</div>', unsafe_allow_html=True)
        
        # Action Buttons (Left Aligned)
        col_copy, col_dl, col_spacer = st.columns([1, 1, 4])
        
        with col_copy:
            copy_to_clipboard(st.session_state.last_result)
            st.caption("Copy to Clipboard")
            
        with col_dl:
            st.download_button(
                label="📥 Download",
                data=st.session_state.last_result,
                file_name="ai_prompt.txt",
                mime="text/plain"
            )

elif menu_item == 'History':
    st.title("📜 Neural Archive")
    if not st.session_state.history:
        st.info("No history found in the database.")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Prompt #{len(st.session_state.history)-i}"):
                st.write(f"**Original:** {item['input']}")
                st.code(item['output'])

elif menu_item == 'Settings':
    st.title("⚙️ System Config")
    st.slider("Processing Temperature", 0.0, 1.0, 0.7)
    st.radio("Model Version", ["Gemini 2.5 Flash", "Gemini 3 Pro"])
    st.success("System is running at 100% capacity.")

st.markdown('</div>', unsafe_allow_html=True)
