import streamlit as st
import google.generativeai as genai
import streamlit_antd_components as sac
from supabase import create_client, Client

# --- 1. CONFIG & DB SETUP ---
st.set_page_config(page_title="Prompt Studio", page_icon="🪄", layout="wide")

# Persistent Client Setup
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    # We initialize without persistence to handle session manually in Streamlit
    return create_client(url, key)

supabase = get_supabase()

try:
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
except:
    st.error("Gemini API Key missing!")

# --- 2. THE UI (Original Legacy Design) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%); background-attachment: fixed; }
    .main-box { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(20px); border-radius: 20px; padding: 30px; border: 1px solid rgba(255, 255, 255, 0.1); }
    div.stButton > button { background-color: #00f2fe !important; color: #050b1a !important; font-weight: bold; border-radius: 10px; width: 100%; border: none; }
    h1, h2, h3, p, span, label { color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "user" not in st.session_state: st.session_state.user = None
if "access_token" not in st.session_state: st.session_state.access_token = None
if "usage_count" not in st.session_state: st.session_state.usage_count = 0
if "last_result" not in st.session_state: st.session_state.last_result = ""

# --- 4. AUTH LOGIC ---
with st.sidebar:
    st.title("🔐 Account")
    if st.session_state.user:
        st.write(f"User: **{st.session_state.user.email}**")
        if st.button("Log Out"):
            st.session_state.user = None
            st.session_state.access_token = None
            st.rerun()
    else:
        mode = st.radio("Mode", ["Login", "Sign Up"], horizontal=True)
        email = st.text_input("Email").strip()
        pw = st.text_input("Password", type="password").strip()
        
        if mode == "Login" and st.button("Sign In"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": pw})
                st.session_state.user = res.user
                st.session_state.access_token = res.session.access_token
                st.rerun()
            except: st.error("Login failed. Check credentials.")
        
        if mode == "Sign Up" and st.button("Create Account"):
            try:
                supabase.auth.sign_up({"email": email, "password": pw})
                st.success("Account created! Now switch to Login.")
            except Exception as e: st.error(f"Error: {e}")

# --- 5. NAVIGATION ---
tab = sac.tabs([
    sac.TabsItem(label='New Chat', icon='chat-square-dots-fill'),
    sac.TabsItem(label='History', icon='clock-fill'),
], align='center', variant='toggle', color='cyan')

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# --- 6. PAGE ROUTING ---
if tab == 'New Chat':
    if not st.session_state.user and st.session_state.usage_count >= 3:
        st.error("🚫 Limit reached! Please login to continue.")
    else:
        if st.session_state.last_result:
            st.code(st.session_state.last_result)
            if st.button("🆕 New Chat"): 
                st.session_state.last_result = ""; st.rerun()
        else:
            prompt_input = st.text_area("Your Idea:", height=150)
            if st.button("GENERATE"):
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt_input)
                st.session_state.last_result = response.text
                st.session_state.usage_count += 1
                
                # Save to DB if logged in
                if st.session_state.user:
                    # Pass the token to authenticate this specific request
                    supabase.postgrest.auth(st.session_state.access_token)
                    supabase.table("user_prompts").insert({
                        "user_id": st.session_state.user.id,
                        "input_text": prompt_input,
                        "output_text": response.text
                    }).execute()
                st.rerun()

elif tab == 'History':
    if not st.session_state.user:
        st.info("Log in to see your history.")
    else:
        try:
            # Re-authenticate client for this session
            supabase.postgrest.auth(st.session_state.access_token)
            data = supabase.table("user_prompts").select("*").order('created_at', descending=True).execute()
            
            if not data.data:
                st.write("No history found. Try generating a prompt while logged in!")
            else:
                for item in data.data:
                    with st.expander(f"Prompt: {item['input_text'][:40]}..."):
                        st.write(f"**Request:** {item['input_text']}")
                        st.code(item['output_text'])
        except Exception as e:
            st.error(f"Could not load history: {e}")

st.markdown('</div>', unsafe_allow_html=True)
