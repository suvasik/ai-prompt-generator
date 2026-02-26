import streamlit as st
import google.generativeai as genai
import streamlit_antd_components as sac
from supabase import create_client, Client

# --- 1. INITIALIZE SUPABASE ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. CONFIG & GENAI ---
st.set_page_config(page_title="Prompt Studio Pro", page_icon="🪄", layout="wide")
genai.configure(api_key=st.secrets["GEMINI_KEY"])

# --- 3. SESSION STATE MANAGEMENT ---
if "usage_count" not in st.session_state: st.session_state.usage_count = 0
if "user" not in st.session_state: st.session_state.user = None
if "history" not in st.session_state: st.session_state.history = []

# --- 4. AUTH FUNCTIONS ---
def sign_up(email, password):
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        st.success("Check your email for confirmation!")
    except Exception as e:
        st.error(f"Error: {e}")

def login(email, password):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user = res.user
        # Fetch history from DB after login
        fetch_history()
        st.rerun()
    except Exception as e:
        st.error("Invalid login credentials")

def fetch_history():
    if st.session_state.user:
        res = supabase.table("user_prompts").select("*").eq("user_id", st.session_state.user.id).execute()
        st.session_state.history = res.data

def save_to_db(prompt_in, prompt_out):
    if st.session_state.user:
        data = {
            "user_id": st.session_state.user.id,
            "input_text": prompt_in,
            "output_text": prompt_out
        }
        supabase.table("user_prompts").insert(data).execute()

# --- 5. UI & NAVIGATION ---
# (Keeping your beautiful gradient CSS from before...)
st.markdown("""<style>...</style>""", unsafe_allow_html=True)

menu_item = sac.tabs([
    sac.TabsItem(label='Generator', icon='magic'),
    sac.TabsItem(label='History', icon='clock-history'),
    sac.TabsItem(label='Account', icon='person-circle'),
], align='center', variant='toggle', color='cyan')

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# --- 6. LOGIC GATING ---
if menu_item == 'Generator':
    # CHECK IF USER IS BLOCKED
    if not st.session_state.user and st.session_state.usage_count >= 3:
        st.warning("🚀 You've reached the Guest limit! Please Login to continue generating and save your history.")
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            e = st.text_input("Email", key="log_e")
            p = st.text_input("Password", type="password", key="log_p")
            if st.button("Login"): login(e, p)
        with tab2:
            e_s = st.text_input("Email", key="sig_e")
            p_s = st.text_input("Password", type="password", key="sig_p")
            if st.button("Create Account"): sign_up(e_s, p_s)
    
    else:
        # NORMAL GENERATOR CODE
        user_input = st.text_area("What are we creating today?")
        if st.button("GENERATE"):
            # 1. Generate AI Content
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(user_input)
            
            # 2. Update logic
            st.session_state.usage_count += 1
            if st.session_state.user:
                save_to_db(user_input, response.text)
            
            st.code(response.text)

elif menu_item == 'History':
    fetch_history() # Refresh history from DB
    for item in st.session_state.history:
        with st.expander(item['created_at']):
            st.write(item['output_text'])

st.markdown('</div>', unsafe_allow_html=True)

