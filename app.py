import streamlit as st
import google.generativeai as genai
import sac # This is streamlit-antd-components

# --- 1. CONFIGURATION & SECRETS ---
GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="Prompt Studio", page_icon="🪄", layout="wide")

# --- 2. CUSTOM CSS FOR THE MENU & THEME ---
st.markdown("""
    <style>
    .stDeployButton {display:none;}
    [data-testid="stSidebar"] {background-color: #0e1117;}
    .main {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
                    url("https://images.unsplash.com/photo-1620641788421-7a1c342ea42e?q=80&w=2548&auto=format&fit=crop");
        background-size: cover;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE INITIALIZATION ---
if "history" not in st.session_state:
    st.session_state.history = []
if "current_response" not in st.session_state:
    st.session_state.current_response = ""
if "page" not in st.session_state:
    st.session_state.page = "New Chat"

# --- 4. SIDEBAR MENU ---
with st.sidebar:
    st.title("🪄 Prompt Studio")
    
    # The Menu Button System
    menu_selection = st.radio(
        "MENU",
        ["✨ New Chat", "📜 View History", "⚙️ Settings"],
        index=0
    )

# --- 5. LOGIC FOR MENU ACTIONS ---

# --- PAGE: SETTINGS ---
if menu_selection == "⚙️ Settings":
    st.header("⚙️ App Settings")
    st.write("Customize your AI experience.")
    model_choice = st.selectbox("Select Model", ["Gemini 2.5 Flash", "Gemini 3 Pro"])
    st.slider("Creativity (Temperature)", 0.0, 1.0, 0.7)
    if st.button("Save Settings"):
        st.success("Settings Updated!")

# --- PAGE: HISTORY ---
elif menu_selection == "📜 View History":
    st.header("📜 Chat History")
    if not st.session_state.history:
        st.info("No prompts generated yet. Start a new chat!")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Prompt #{len(st.session_state.history) - i}: {item['original'][:30]}..."):
                st.write(f"**Original:** {item['original']}")
                st.code(item['enhanced'])
        if st.button("🗑️ Clear All History"):
            st.session_state.history = []
            st.rerun()

# --- PAGE: NEW CHAT (Main App) ---
elif menu_selection == "✨ New Chat":
    st.title("🪄 Enhance Your Prompt")
    
    user_input = st.text_area("Enter your basic sentence:", placeholder="What do you want to create?")
    
    col1, col2 = st.columns([1, 5])
    
    with col1:
        if st.button("Generate"):
            if user_input:
                with st.spinner("Writing..."):
                    try:
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        response = model.generate_content(f"Enhance this prompt professionally: {user_input}")
                        
                        # Save to state
                        st.session_state.current_response = response.text
                        st.session_state.history.append({
                            "original": user_input,
                            "enhanced": response.text
                        })
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Please enter text.")

    if st.session_state.current_response:
        st.markdown("### ✨ Enhanced Result")
        st.info(st.session_state.current_response)
        
        # Action Buttons for the result
        if st.button("🆕 Start Fresh"):
            st.session_state.current_response = ""
            st.rerun()
