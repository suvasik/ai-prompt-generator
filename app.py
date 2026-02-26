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
    st.error("Missing configuration keys in Secrets!")

# --- 2. THE UI (Legacy Gradient + Glassmorphism) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        background-attachment: fixed;
    }
    .main-box {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 25px;
        padding: 40px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
    }
    div.stButton > button {
        background-color: #00f2fe !important;
        color: #050b1a !important;
        border-radius: 12px !important;
        font-weight: 900 !important;
        width: 100%;
    }
    h1, h2, h3, p, label, span { color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "usage_count" not in st.session_state: st.session_state.usage_count = 0
if "user" not in st.session_state: st.session_state.user = None
if "history" not in st.session_state: st.session_state.history = []
if "last_result" not in st.session_state: st.session_state.last_result = ""

# --- 4. SIDEBAR LOGIN ---
with st.sidebar:
    st.title("🔑 Access")
    if st.session_state.user:
        st.success(f"Logged in: {st.session_state.user.email}")
        if st.button("Log Out"):
            st.session_state.user = None
            st.rerun()
    else:
        st.info(f"Guest Usage: {st.session_state.usage_count}/3")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login Directly"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = res.user
                    st.rerun()
                except:
                    st.error("Login failed. Check credentials.")

# --- 5. MAIN NAVIGATION ---
menu_item = sac.tabs([
    sac.TabsItem(label='New Chat', icon='chat-square-dots-fill'),
    sac.TabsItem(label='History', icon='clock-fill'),
    sac.TabsItem(label='Account', icon='person-bounding-box'),
], align='center', variant='toggle', color='cyan')

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# --- 6. TAB LOGIC ---
if menu_item == 'New Chat':
    if not st.session_state.user and st.session_state.usage_count >= 3:
        st.error("🚫 Guest limit reached! Please use the sidebar to login.")
    else:
        if st.session_state.last_result:
            st.code(st.session_state.last_result)
            c1, c2 = st.columns(2)
            if c1.button("🆕 Clear & New"): 
                st.session_state.last_result = ""; st.rerun()
            c2.download_button("📥 Download", st.session_state.last_result, "prompt.txt")
        else:
            u_input = st.text_area("What should the AI write?", height=150)
            if st.button("GENERATE MASTERPIECE"):
                model = genai.GenerativeModel('gemini-2.5-flash')
                resp = model.generate_content(u_input)
                st.session_state.last_result = resp.text
                st.session_state.usage_count += 1
                if st.session_state.user:
                    supabase.table("user_prompts").insert({
                        "user_id": st.session_state.user.id,
                        "input_text": u_input, "output_text": resp.text
                    }).execute()
                st.rerun()

elif menu_item == 'History':
    if not st.session_state.user:
        st.warning("Please login via the sidebar to view your permanent history.")
    else:
        res = supabase.table("user_prompts").select("*").eq("user_id", st.session_state.user.id).execute()
        for item in res.data:
            with st.expander(f"Prompt: {item['input_text'][:30]}..."):
                st.code(item['output_text'])

elif menu_item == 'Account':
    st.subheader("User Statistics")
    st.write(f"Total Prompts Generated: {st.session_state.usage_count}")
    if st.button("🗑️ Reset Local Counter"):
        st.session_state.usage_count = 0
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
