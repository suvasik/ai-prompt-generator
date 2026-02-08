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

# --- CYBER UI CSS (Left Aligned & Glassmorphism) ---
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
    /* Left-align buttons and style them */
    .stButton > button {
        width: auto !important;
        background: linear-gradient(90deg, #6c5ce7, #00d2ff) !important;
        color: white !important;
        border: none !important;
        padding: 10px 25px !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

if "history" not in st.session_state: st.session_state.history = []
if "last_result" not in st.session_state: st.session_state.last_result = ""

# --- SIDEBAR (Left Menu) ---
with st.sidebar:
    st.markdown("# 🪄 Menu")
    menu_item = sac.menu([
        sac.MenuItem('New Chat', icon='plus-circle'),
        sac.MenuItem('History', icon='clock-history'),
        sac.MenuItem('Settings', icon='sliders'),
    ], color='indigo', variant='filled')

# --- MAIN PAGE CONTENT ---
st.markdown('<div class="main-box">', unsafe_allow_html=True)

if menu_item == 'New Chat':
    st.title("🚀 AI Prompt Generator")
    user_input = st.text_area("Enter your idea:", placeholder="A futuristic city in space...", height=100)
    
    # Generate Button (Left Aligned)
    if st.button("Generate Masterpiece"):
        if user_input:
            with st.spinner("Neural Processing..."):
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(f"Expand this into a professional prompt: {user_input}")
                    st.session_state.last_result = response.text
                    st.session_state.history.append({"input": user_input, "output": response.text})
                except Exception as e:
                    st.error(f"Error: {e}")

    # Result Section
    if st.session_state.last_result:
        st.subheader("Enhanced Result")
        # Native Streamlit code block provides a COPY button automatically in the top right
        st.code(st.session_state.last_result, language="text")
        
        # Download Button (Left Aligned)
        col1, col2 = st.columns([1, 4])
        with col1:
            st.download_button(
                label="📥 Download .txt",
                data=st.session_state.last_result,
                file_name="ai_prompt.txt",
                mime="text/plain"
            )

elif menu_item == 'History':
    st.title("📜 Neural Archive")
    if not st.session_state.history:
        st.info("No history found.")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Prompt #{len(st.session_state.history)-i}"):
                st.write(f"**Your Input:** {item['input']}")
                st.code(item['output'], language="text")

elif menu_item == 'Settings':
    st.title("⚙️ System Config")
    st.slider("Processing Temperature", 0.0, 1.0, 0.7)
    st.radio("Current Model", ["Gemini 2.5 Flash (Active)", "Gemini 3 Pro"])

st.markdown('</div>', unsafe_allow_html=True)
