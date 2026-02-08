import streamlit as st
import google.generativeai as genai
import base64

# --- CONFIGURATION ---
GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

# --- 1. SETTINGS & CSS (The "Attractive" Part) ---
st.set_page_config(page_title="Prompt Genius", page_icon="🪄", layout="wide")

def local_css():
    st.markdown("""
        <style>
        /* Hide the Deploy button and Hamburger menu */
        .stDeployButton {display:none;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Background Image */
        .stApp {
            background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                        url("https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop");
            background-size: cover;
        }

        /* Glassmorphism containers */
        .stTextInput, .stTextArea, div.stButton > button {
            background-color: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: white !important;
            border-radius: 10px !important;
        }
        
        /* Titles */
        h1, h2, h3, p {
            color: white !important;
            font-family: 'Inter', sans-serif;
        }
        </style>
    """, unsafe_allow_html=True)

local_css()

# --- 2. SESSION STATE (The History Feature) ---
if "history" not in st.session_state:
    st.session_state.history = []

def enhance_prompt(user_text):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        meta_prompt = f"Act as a professional Prompt Engineer. Enhance this: '{user_text}'. Provide a high-quality prompt with instructions and context."
        response = model.generate_content(meta_prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

# --- 3. SIDEBAR (History Display) ---
with st.sidebar:
    st.title("📜 History")
    if not st.session_state.history:
        st.write("No history yet.")
    else:
        for idx, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Prompt {len(st.session_state.history) - idx}"):
                st.write(f"**Original:** {item['original']}")
                st.code(item['enhanced'])
    
    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()

# --- 4. MAIN INTERFACE ---
st.title("🪄 Prompt Genius")
st.markdown("##### Transform simple ideas into engineering masterpieces.")

col1, col2 = st.columns([2, 1])

with col1:
    user_input = st.text_area("What is your basic idea?", placeholder="e.g. A futuristic city in Mars", height=150)
    
    if st.button("✨ Enhance My Prompt"):
        if user_input:
            with st.spinner("Analyzing and refining..."):
                enhanced_text = enhance_prompt(user_input)
                
                # Save to history
                st.session_state.history.append({
                    "original": user_input,
                    "enhanced": enhanced_text
                })
                
                st.success("Done!")
                st.text_area("Your New Prompt:", value=enhanced_text, height=300)
                st.button("📋 Copy text (Manual)")
        else:
            st.warning("Please enter some text first!")

with col2:
    st.write("### Quick Tips")
    st.info("""
    - **Be Specific:** Tell the AI the tone you want.
    - **Format:** Ask for bullet points or code.
    - **Persona:** Tell the AI to 'Act as...'

    """)
