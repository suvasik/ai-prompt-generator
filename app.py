import streamlit as st
import google.generativeai as genai
import streamlit_antd_components as sac
from supabase import create_client
import streamlit.components.v1 as components

# --- 1. CONFIG & DB SETUP ---
st.set_page_config(page_title="Prompt Studio Pro", page_icon="🪄", layout="wide")

def get_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except: return None

supabase = get_supabase()
genai.configure(api_key=st.secrets["GEMINI_KEY"])

# --- 2. CSS ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top right, #1e293b, #0f172a); color: #f8fafc; }
    .main-box { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(15px); border-radius: 28px; padding: 40px; border: 1px solid rgba(255, 255, 255, 0.1); margin-top: 10px; }
    .stTextArea textarea { background: rgba(15, 23, 42, 0.8) !important; color: #22d3ee !important; border-radius: 16px !important; }
    div.stButton > button { background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%) !important; color: white !important; font-weight: 800 !important; border-radius: 14px !important; border: none !important; }
    h1, h2, h3 { background: linear-gradient(90deg, #22d3ee, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
for key in ["user", "access_token", "usage_count", "last_result"]:
    if key not in st.session_state:
        st.session_state[key] = 0 if key == "usage_count" else None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("👤 Access")
    if st.session_state.user:
        st.success(f"In: {st.session_state.user.email}")
        if st.button("Logout"): st.session_state.user = None; st.rerun()
    else:
        mode = st.radio("Portal", ["Login", "Sign Up"], horizontal=True)
        email = st.text_input("Email").strip()
        pw = st.text_input("Password", type="password").strip()
        if st.button("Enter"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": pw})
                st.session_state.user = res.user
                st.session_state.access_token = res.session.access_token
                st.rerun()
            except: st.error("Failed")

# --- 5. NAVIGATION (Fixed Location) ---
try:
    tab = sac.tabs([
        sac.TabsItem(label='Generator', icon='magic'),
        sac.TabsItem(label='Vault', icon='safe2'),
    ], color='cyan', index=0)
except:
    tab = "Generator"

# --- 6. ROUTING ---
current_tab = str(tab)

if current_tab == 'Generator':
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    with st.expander("📖 Guide"):
        st.info("Enter idea -> Build -> Copy Result")
    
    if not st.session_state.user and st.session_state.usage_count >= 3:
        st.warning("Limit reached. Please login.")
    else:
        if st.session_state.last_result:
            st.code(st.session_state.last_result)
            if st.button("New"): st.session_state.last_result = ""; st.rerun()
        else:
            p_input = st.text_area("Your idea:", height=150)
            if st.button("GENERATE"):
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content("Engineer this prompt: " + p_input)
                st.session_state.last_result = response.text
                st.session_state.usage_count += 1
                if st.session_state.user:
                    supabase.table("user_prompts").insert({"user_id": st.session_state.user.id, "input_text": p_input, "output_text": response.text}).execute()
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif current_tab == 'Vault':
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    st.title("Vault")
    # ... vault logic ...
    st.markdown('</div>', unsafe_allow_html=True)
