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

# --- 2. STABLE BACKGROUND URL ---
# I am using a stable high-quality AI/Tech background link here
bg_img_url = "https://images.unsplash.com/photo-1620712943543-bcc4628c9757?q=80&w=1920&auto=format&fit=crop"

st.markdown(f"""
    <style>
    .stDeployButton {{ display:none; }}
    footer {{ visibility: hidden; }}
    header {{ visibility: hidden; }}

    /* THE BACKGROUND FIX */
    .stApp {{
        background: linear-gradient(rgba(5, 11, 26, 0.75), rgba(5, 11, 26, 0.75)), 
                    url("{bg_img_url}");
        background-size: cover !important;
        background-position: center center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }}

    /* MAIN CONTAINER (Glassmorphism) */
    .main-box {{
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 40px;
        margin-top: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }}

    /* NEON CYAN BUTTONS */
    div.stButton > button {{
        background-color: #00f2fe !important;
        color: #050b1a !important;
        border: 2px solid #ffffff !important;
        padding: 12px 35px !important;
        border-radius: 12px !important;
        font-weight: 900 !important;
        box-shadow: 0px 0px 20px rgba(0, 242, 254, 0.6) !important;
    }}

    div.stButton > button:hover {{
        background-color: #ffffff !important;
        box-shadow: 0px 0px 30px rgba(255, 255, 255, 1) !important;
        transform: scale(1.03);
    }}

    /* TEXT STYLES */
    h1, h2, h3, p, label, span {{
        color: #ffffff !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }}

    /* INPUT TEXT AREA */
    .stTextArea textarea {{
        background: rgba(0, 0, 0, 0.6) !important;
        color: white !important;
        border: 1px solid rgba(0, 242, 254, 0.5) !important;
        border-radius: 10px;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "history" not in st.session_state: st.session_state.history = []
if "last_result" not in st.session_state: st.session_state.last_result = ""

# --- 4. TOP NAVIGATION ---
# Centers the menu items
col_nav_1, col_nav_2, col_nav_3 = st.columns([1, 2, 1])
with col_nav_2:
    menu_item = sac.tabs([
        sac.TabsItem(label='New Chat', icon='chat-square-text-fill'),
        sac.TabsItem(label='History', icon='clock-fill'),
        sac.TabsItem(label='Settings', icon='gear-fill'),
    ], align='center', variant='toggle', color='cyan', index=0)

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# --- 5. LOGIC ---
if menu_item == 'New Chat':
    st.title("🚀 Prompt Generator")
    
    if st.session_state.last_result:
        st.subheader("✨ Enhanced Result")
        st.code(st.session_state.last_result, language="text")
        
        col1, col2, _ = st.columns([1, 1, 4])
        with col1:
            if st.button("🆕 New Chat"):
                st.session_state.last_result = ""
                st.rerun()
        with col2:
            st.download_button("📥 Download", st.session_state.last_result, file_name="ai_prompt.txt")
            
    else:
        user_input = st.text_area("Your Idea:", placeholder="e.g., A cyborg wolf in a neon forest...", height=150)
        if st.button("GENERATE MASTERPIECE"):
            if user_input:
                with st.spinner("Gemini 2.5 is crafting..."):
                    try:
                        model = genai.GenerativeModel('gemini-2.5-flash') 
                        response = model.generate_content(f"Expand this into a professional AI prompt: {user_input}")
                        st.session_state.last_result = response.text
                        st.session_state.history.append({"input": user_input, "output": response.text})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

elif menu_item == 'History':
    st.title("📜 Archive")
    if not st.session_state.history:
        st.info("No records yet. Start a chat above!")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Prompt #{len(st.session_state.history)-i}"):
                st.write(f"**Input:** {item['input']}")
                st.code(item['output'], language="text")

elif menu_item == 'Settings':
    st.title("⚙️ System Settings")
    if st.button("🗑️ Reset All Data"):
        st.session_state.history = []
        st.session_state.last_result = ""
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
