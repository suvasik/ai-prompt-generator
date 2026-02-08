import streamlit as st
import google.generativeai as genai
import streamlit_antd_components as sac

# --- CONFIGURATION ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except:
    st.error("API Key not found in Secrets!")

st.set_page_config(page_title="Prompt Studio", page_icon="🪄", layout="wide")

# --- CYBERPUNK GLASSMORPHISM CSS ---
st.markdown("""
    <style>
    /* Hide Default Elements */
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Background with AI/Tech Imagery */
    .stApp {
        background: linear-gradient(rgba(10, 10, 35, 0.8), rgba(10, 10, 35, 0.8)), 
                    url("https://images.unsplash.com/photo-1677442136019-21780ecad995?q=80&w=2000&auto=format&fit=crop");
        background-size: cover;
        background-attachment: fixed;
    }

    /* Main Container Glass Effect */
    .main-box {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }

    /* Gradient Text & Headers */
    .gradient-text {
        background: linear-gradient(90deg, #ffffff, #a29bfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        font-size: 3rem !important;
    }

    /* Custom Input Styling */
    .stTextArea textarea {
        background: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid #4834d4 !important;
        color: white !important;
        border-radius: 10px !important;
    }

    /* Glowing Button */
    div.stButton > button {
        background: linear-gradient(90deg, #6c5ce7, #00d2ff) !important;
        color: white !important;
        border: none !important;
        padding: 15px 30px !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        transition: 0.3s ease all !important;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    div.stButton > button:hover {
        box-shadow: 0 0 20px rgba(0, 210, 255, 0.6) !important;
        transform: translateY(-2px);
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: rgba(10, 10, 30, 0.9) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session States
if "history" not in st.session_state: st.session_state.history = []
if "generated_prompt" not in st.session_state: st.session_state.generated_prompt = ""

# --- SIDEBAR MENU ---
with st.sidebar:
    st.markdown("<h2 style='color:white; margin-bottom:20px;'>🪄 Navigation</h2>", unsafe_allow_html=True)
    menu_item = sac.menu([
        sac.MenuItem('New Chat', icon='stars'),
        sac.MenuItem('History', icon='archive'),
        sac.MenuItem('Settings', icon='sliders'),
    ], color='indigo', variant='filled')

# --- MAIN CONTENT WRAPPER ---
st.markdown('<div class="main-box">', unsafe_allow_html=True)

if menu_item == 'New Chat':
    st.markdown('<h1 class="gradient-text">Prompt Studio</h1>', unsafe_allow_html=True)
    st.markdown("<p style='color: #b2bec3; font-size: 1.2rem;'>Transforming Ideas into AI Art</p>", unsafe_allow_html=True)
    st.write("---")
    
    user_input = st.text_area("What is your basic idea?", placeholder="e.g. A cybernetic owl in bioluminescent forest", height=120)
    
    if st.button("Generate Masterpiece"):
        if user_input:
            with st.spinner("Processing Neural Networks..."):
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(f"Act as a professional Prompt Engineer. Expand this into a detailed, structured AI prompt: {user_input}")
                    st.session_state.generated_prompt = response.text
                    st.session_state.history.append({"input": user_input, "output": response.text})
                except Exception as e:
                    st.error(f"Error: {e}")
    
    if st.session_state.generated_prompt:
        st.markdown("### ⚡ Enhanced Result")
        st.info(st.session_state.generated_prompt)

elif menu_item == 'History':
    st.markdown('<h1 class="gradient-text">Archive</h1>', unsafe_allow_html=True)
    if not st.session_state.history:
        st.info("No records found in the database.")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Entry {len(st.session_state.history)-i}"):
                st.write(f"**Input:** {item['input']}")
                st.code(item['output'])

elif menu_item == 'Settings':
    st.markdown('<h1 class="gradient-text">System Settings</h1>', unsafe_allow_html=True)
    st.select_slider("Neural Processing Depth", options=["Low", "Standard", "Deep", "Quantum"])
    st.checkbox("Enable Auto-History", value=True)

st.markdown('</div>', unsafe_allow_html=True)
