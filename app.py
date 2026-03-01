import streamlit as st
import google.generativeai as genai
import streamlit_antd_components as sac
from supabase import create_client, Client

# --- 1. CONFIG & DB SETUP ---
st.set_page_config(page_title="Prompt Studio", page_icon="🪄", layout="wide")

try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
except Exception as e:
    st.error("Check your Streamlit Secrets for URL and API Key!")

# --- 2. THE UI (Legacy Gradient + Glassmorphism) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%); background-attachment: fixed; }
    .main-box { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(20px); border-radius: 25px; padding: 40px; box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5); border: 1px solid rgba(255, 255, 255, 0.1); }
    div.stButton > button { background-color: #00f2fe !important; color: #050b1a !important; border-radius: 12px !important; font-weight: 900 !important; width: 100%; }
    h1, h2, h3, p, label, span { color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "usage_count" not in st.session_state: st.session_state.usage_count = 0
if "user" not in st.session_state: st.session_state.user = None
if "last_result" not in st.session_state: st.session_state.last_result = ""

# --- 4. SIDEBAR AUTH (Sign Up & Login) ---
with st.sidebar:
    st.title("🔐 User Portal")
    if st.session_state.user:
        st.success(f"Welcome, {st.session_state.user.email}")
        if st.button("Log Out"):
            st.session_state.user = None
            st.rerun()
    else:
        auth_mode = st.radio("Choose Mode", ["Login", "Sign Up"], horizontal=True)
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        if auth_mode == "Login":
            if st.button("Sign In"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email.strip(), "password": password.strip()})
                    st.session_state.user = res.user
                    st.rerun()
                except Exception as e:
                    st.error(f"Login Failed: {str(e)}")
        else:
            if st.button("Create Account"):
                try:
                    # sign_up creates the user in Supabase
                    res = supabase.auth.sign_up({"email": email.strip(), "password": password.strip()})
                    st.success("Account created! You can now log in.")
                except Exception as e:
                    st.error(f"Sign Up Failed: {str(e)}")

# --- 5. MAIN NAVIGATION ---
menu_item = sac.tabs([
    sac.TabsItem(label='New Chat', icon='chat-square-dots-fill'),
    sac.TabsItem(label='History', icon='clock-fill'),
], align='center', variant='toggle', color='cyan')

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# --- 6. PAGE LOGIC ---
if menu_item == 'New Chat':
    # Logic gating: Guest limit of 3
    if not st.session_state.user and st.session_state.usage_count >= 3:
        st.warning("⚠️ Limit reached! Please Sign Up or Login via the sidebar to continue.")
    else:
        if st.session_state.last_result:
            st.code(st.session_state.last_result)
            if st.button("🆕 Start New Chat"):
                st.session_state.last_result = ""; st.rerun()
        else:
            u_input = st.text_area("What should the AI generate?", height=150)
            if st.button("GENERATE MASTERPIECE"):
                model = genai.GenerativeModel('gemini-2.5-flash')
                resp = model.generate_content(u_input)
                st.session_state.last_result = resp.text
                st.session_state.usage_count += 1
                
                # SAVE TO DB IF LOGGED IN
                if st.session_state.user:
                    supabase.table("user_prompts").insert({
                        "user_id": st.session_state.user.id,
                        "input_text": u_input, "output_text": resp.text
                    }).execute()
                st.rerun()

elif menu_item == 'History':
    if not st.session_state.user:
        st.info("Log in to access your permanent history.")
    else:
        # Pull history from Supabase table
        data = supabase.table("user_prompts").select("*").eq("user_id", st.session_state.user.id).execute()
        for item in data.data:
            with st.expander(f"Prompt: {item['input_text'][:40]}..."):
                st.code(item['output_text'])

st.markdown('</div>', unsafe_allow_html=True)
