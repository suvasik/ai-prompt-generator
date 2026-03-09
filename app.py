import streamlit as st
from google import genai
from google.genai import types
from supabase import create_client, Client
import streamlit.components.v1 as components

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(page_title="Prompt Architect", page_icon="🏗️", layout="wide")

# Custom CSS for Glassmorphism
st.markdown("""
    <style>
    .stApp { background: #0f172a; color: white; }
    .main-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #06b6d4, #3b82f6);
        color: white; border: none; border-radius: 10px; height: 3em;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. BACKEND CONNECTIONS ---
@st.cache_resource
def init_connection():
    # Direct initialization to avoid 'ClientOptions' attribute errors
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()
client = genai.Client(api_key=st.secrets["GEMINI_KEY"])

# --- 3. SESSION STATE ---
if "user" not in st.session_state: st.session_state.user = None
if "history" not in st.session_state: st.session_state.history = []

# --- 4. AUTHENTICATION SIDEBAR ---
with st.sidebar:
    st.title("🔐 Access Portal")
    if not st.session_state.user:
        auth_mode = st.radio("Mode", ["Login", "Sign Up"])
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        if st.button("Submit"):
            try:
                if auth_mode == "Login":
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                else:
                    res = supabase.auth.sign_up({"email": email, "password": password})
                st.session_state.user = res.user
                st.rerun()
            except Exception as e:
                st.error(f"Auth Error: {e}")
    else:
        st.success(f"Welcome, {st.session_state.user.email}")
        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()

# --- 5. CORE GENERATOR LOGIC ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.title("🪄 AI Prompt Architect")
st.caption("Transform simple ideas into professional-grade AI instructions.")

user_input = st.text_area("Enter your basic idea:", placeholder="e.g. A workout plan for beginners")

if st.button("🚀 ARCHITECT PROMPT"):
    if user_input:
        with st.spinner("Engineering your prompt..."):
            # SYSTEM INSTRUCTION: This is the 'secret sauce' for your project
            sys_msg = "You are a Master Prompt Engineer. Take the user's idea and rewrite it into a professional prompt including: Persona, Context, Task, Constraints, and Output Format."
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_input,
                config=types.GenerateContentConfig(system_instruction=sys_msg)
            )
            
            generated_prompt = response.text
            st.session_state.last_result = generated_prompt
            
            # Save to Supabase Library
            if st.session_state.user:
                supabase.table("user_prompts").insert({
                    "user_id": st.session_state.user.id,
                    "input_text": user_input,
                    "output_text": generated_prompt
                }).execute()
    else:
        st.warning("Please enter an idea first!")

# --- 6. RESULT DISPLAY ---
if "last_result" in st.session_state:
    st.subheader("✅ Optimized Prompt")
    st.code(st.session_state.last_result, language="markdown")
    
    # JavaScript Copy Feature
    copy_code = f"""
    <button onclick="navigator.clipboard.writeText(`{st.session_state.last_result.replace('`','\\`')}`)" 
    style="padding: 10px; background: #22c55e; color: white; border: none; border-radius: 5px; cursor: pointer;">
    📋 Copy to Clipboard
    </button>
    """
    components.html(copy_code, height=50)

st.markdown('</div>', unsafe_allow_html=True)
