import streamlit as st
from google import genai
from google.genai import types
from supabase import create_client
import streamlit.components.v1 as components

# --- 1. CONFIG & SYSTEM ARCHITECT PROMPT ---
st.set_page_config(page_title="Prompt Architect Pro", page_icon="🏗️", layout="wide")

# The "Brain" of Choice B: Forces Gemini to act as a Prompt Engineer
ARCHITECT_SYSTEM_PROMPT = """
You are a Professional Prompt Engineer. Your ONLY task is to transform user ideas into high-quality, structured AI prompts.

When the user provides an idea, generate a response following this EXACT structure:
1. **Persona**: Who should the AI act as? (e.g., Expert Data Scientist, Creative Writer)
2. **Context**: What background info does the AI need to understand the goal?
3. **Task**: What is the specific, actionable goal?
4. **Constraints**: What are the limits (word count, tone, things to avoid)?
5. **Output Format**: How should the result look (Table, Markdown, Code, etc.)?

Output the final result as a clean, copyable block of Markdown text. Do NOT be conversational.
"""

# --- 2. BACKEND CONNECTIONS ---
@st.cache_resource
def init_supabase():
    # Direct initialization to avoid 'ClientOptions' errors
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()
gemini_client = genai.Client(api_key=st.secrets["GEMINI_KEY"])

# --- 3. CUSTOM GLASSMORPHISM UI ---
st.markdown("""
    <style>
    .stApp { background: #0f172a; color: white; }
    .main-box { 
        background: rgba(255, 255, 255, 0.05); 
        backdrop-filter: blur(15px); 
        border-radius: 20px; 
        padding: 30px; 
        border: 1px solid rgba(255, 255, 255, 0.1); 
    }
    div.stButton > button { 
        background: linear-gradient(45deg, #06b6d4, #3b82f6) !important;
        color: white !important; font-weight: bold !important; 
        border-radius: 10px !important; border: none !important;
    }
    .stTextArea textarea { background: #1e293b !important; color: #22d3ee !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. SESSION STATE & AUTH ---
if "user" not in st.session_state: st.session_state.user = None
if "last_result" not in st.session_state: st.session_state.last_result = ""
if "reset_mode" not in st.session_state: st.session_state.reset_mode = False

with st.sidebar:
    st.title("👤 User Portal")
    if st.session_state.user:
        st.success(f"Active: {st.session_state.user.email}")
        if st.button("Logout"):
            st.session_state.user = None; st.rerun()
    else:
        auth_mode = st.radio("Access", ["Login", "Sign Up"])
        email = st.text_input("Email")
        pw = st.text_input("Password", type="password")
        if st.button("Authenticate"):
            try:
                if auth_mode == "Login":
                    res = supabase.auth.sign_in_with_password({"email": email, "password": pw})
                else:
                    res = supabase.auth.sign_up({"email": email, "password": pw})
                st.session_state.user = res.user
                st.rerun()
            except Exception as e: st.error(f"Error: {e}")

# --- 5. MAIN APP INTERFACE ---
st.markdown('<div class="main-box">', unsafe_allow_html=True)
st.title("🏗️ AI Prompt Architect")
st.write("Convert vague ideas into high-performance professional prompts.")

user_idea = st.text_area("What is your basic idea?", placeholder="e.g., Create a social media plan for a coffee shop", height=120)

col1, col2 = st.columns([1, 4])
with col1:
    generate_btn = st.button("GENERATE")

if generate_btn:
    if user_idea:
        with st.spinner("Engineering Professional Prompt..."):
            try:
                # Choice B: Calling Gemini with the System Instruction
                response = gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=user_idea,
                    config=types.GenerateContentConfig(system_instruction=ARCHITECT_SYSTEM_PROMPT)
                )
                st.session_state.last_result = response.text
                
                # Save to Supabase Library if logged in
                if st.session_state.user:
                    supabase.table("user_prompts").insert({
                        "user_id": st.session_state.user.id,
                        "input_text": user_idea,
                        "output_text": response.text
                    }).execute()
            except Exception as e:
                st.error(f"Generation Failed: {e}")
    else:
        st.warning("Please enter an idea first.")

# --- 6. RESULTS & UTILITY ---
if st.session_state.last_result:
    st.divider()
    st.subheader("🚀 Engineered Result")
    st.code(st.session_state.last_result, language="markdown")
    
    # JavaScript Copy Button
    safe_text = st.session_state.last_result.replace("`", "\\`").replace("'", "\\'")
    copy_html = f"""
        <button onclick="navigator.clipboard.writeText(`{safe_text}`).then(() => alert('Copied!'))" 
        style="width: 100%; height: 45px; background: #22c55e; color: white; border: none; border-radius: 10px; cursor: pointer; font-weight: bold;">
        📋 COPY TO CLIPBOARD
        </button>
    """
    components.html(copy_html, height=60)
    
    if st.button("🆕 New Architect Job"):
        st.session_state.last_result = ""; st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# --- 7. LIBRARY SECTION (Visible if Logged In) ---
if st.session_state.user:
    st.write("---")
    st.subheader("📚 Your Prompt Library")
    try:
        data = supabase.table("user_prompts").select("*").eq("user_id", st.session_state.user.id).order('created_at', desc=True).execute()
        for item in data.data:
            with st.expander(f"📦 {item['input_text'][:50]}..."):
                st.write(f"**Original Idea:** {item['input_text']}")
                st.code(item['output_text'])
    except:
        st.info("Start generating to build your library!")
