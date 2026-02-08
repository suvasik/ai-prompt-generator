import streamlit as st
import google.generativeai as genai
import streamlit_antd_components as sac

# --- 1. CONFIGURATION ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except:
    st.error("API Key not found in Secrets!")

st.set_page_config(page_title="Prompt Studio", page_icon="🪄", layout="wide")

# Initialize Session States
if "history" not in st.session_state:
    st.session_state.history = []
if "generated_prompt" not in st.session_state:
    st.session_state.generated_prompt = ""

# --- 2. SIDEBAR MENU ---
with st.sidebar:
    st.title("🪄 AI Menu")
    menu_item = sac.menu([
        sac.MenuItem('New Chat', icon='plus-circle-fill'),
        sac.MenuItem('History', icon='clock-history'),
        sac.MenuItem('Settings', icon='gear-fill'),
    ], format_func='title', open_all=True)

# --- 3. DYNAMIC BACKGROUND COLORS (CSS) ---
# We define different gradients for each page
bg_colors = {
    'New Chat': "linear-gradient(135deg, #1e1e2f 0%, #2d3436 100%)", # Dark Slate
    'History': "linear-gradient(135deg, #2c3e50 0%, #000000 100%)",  # Midnight Blue
    'Settings': "linear-gradient(135deg, #0f0c29 0%, #302b63 100%)" # Deep Purple
}

selected_bg = bg_colors.get(menu_item, "#0e1117")

st.markdown(f"""
    <style>
    .stApp {{
        background: {selected_bg};
        color: white;
    }}
    .stDeployButton {{display:none;}}
    /* Style inputs to look better on dark backgrounds */
    .stTextArea textarea {{
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. APP LOGIC ---

if menu_item == 'New Chat':
    st.title("✨ Create an Enhanced Prompt")
    st.write("Current Theme: **Generator Mode**")
    
    user_input = st.text_area("What is your basic idea?", placeholder="e.g. A cat drinking tea in space", height=100)
    
    if st.button("Generate Masterpiece"):
        if user_input:
            with st.spinner("AI is thinking..."):
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(f"Act as a Prompt Engineer. Expand this into a high-quality AI prompt: {user_input}")
                    st.session_state.generated_prompt = response.text
                    st.session_state.history.append({"input": user_input, "output": response.text})
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a sentence first.")

    if st.session_state.generated_prompt:
        st.subheader("Enhanced Result:")
        st.info(st.session_state.generated_prompt)

elif menu_item == 'History':
    st.title("📜 Past Prompts")
    st.write("Current Theme: **Archive Mode**")
    if not st.session_state.history:
        st.info("Your history is empty.")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Prompt {len(st.session_state.history)-i}"):
                st.write(f"**Input:** {item['input']}")
                st.code(item['output'])

elif menu_item == 'Settings':
    st.title("⚙️ App Settings")
    st.write("Current Theme: **Configuration Mode**")
    st.color_picker("Pick a custom accent color", "#00FFAA")
    st.toggle("Enable Advanced Logic")
    st.button("Reset App Cache")
