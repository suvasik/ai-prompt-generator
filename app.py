import streamlit as st
import google.generativeai as genai
import streamlit_antd_components as sac
from supabase import create_client, Client
from streamlit_extras.stylable_container import stylable_container # Optional but nice

# --- 1. CONFIG & DB SETUP ---
st.set_page_config(page_title="Prompt Studio Pro", page_icon="🪄", layout="wide")

def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()
genai.configure(api_key=st.secrets["GEMINI_KEY"])

# --- 2. THE UI & CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%); background-attachment: fixed; }
    .main-box { 
        background: rgba(255, 255, 255, 0.07); 
        backdrop-filter: blur(25px); 
        border-radius: 25px; 
        padding: 40px; 
        border: 1px solid rgba(255, 255, 255, 0.1); 
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
    }
    /* Glowing Button Styles */
    div.stButton > button { 
        background: linear-gradient(45deg, #00f2fe, #4facfe) !important;
        color: #050b1a !important; font-weight: 800 !important; 
        border-radius: 12px !important; border: none !important;
        transition: 0.3s all ease !important;
    }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0, 242, 254, 0.4); }
    h1, h2, h3, p, span, label { color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "user" not in st.session_state: st.session_state.user = None
if "access_token" not in st.session_state: st.session_state.access_token = None
if "usage_count" not in st.session_state: st.session_state.usage_count = 0
if "last_result" not in st.session_state: st.session_state.last_result = ""

# --- 4. SIDEBAR AUTH ---
with st.sidebar:
    st.title("👤 Account")
    if st.session_state.user:
        st.success(f"Logged in: {st.session_state.user.email}")
        if st.button("Logout"):
            st.session_state.user = None; st.session_state.access_token = None; st.rerun()
    else:
        st.write(f"Guest Usage: {st.session_state.usage_count}/3")
        st.progress(st.session_state.usage_count / 3)
        mode = st.radio("Mode", ["Login", "Sign Up"], horizontal=True)
        email = st.text_input("Email").strip()
        pw = st.text_input("Password", type="password").strip()
        
        if mode == "Login" and st.button("Sign In"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": pw})
                st.session_state.user = res.user
                st.session_state.access_token = res.session.access_token
                st.rerun()
            except: st.error("Login failed.")
        
        if mode == "Sign Up" and st.button("Create Account"):
            try:
                supabase.auth.sign_up({"email": email, "password": pw})
                st.success("Created! Now Login.")
            except Exception as e: st.error(f"Error: {e}")

# --- 5. NAVIGATION ---
tab = sac.tabs([
    sac.TabsItem(label='Generator', icon='magic'),
    sac.TabsItem(label='My Library', icon='folder2-open'),
], align='center', variant='toggle', color='cyan')

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# --- 6. PAGE ROUTING ---
if tab == 'Generator':
    if not st.session_state.user and st.session_state.usage_count >= 3:
        st.error("💡 Free limit reached. Please login!")
    else:
        if st.session_state.last_result:
            st.markdown("### ✨ AI Result")
            st.code(st.session_state.last_result, language="markdown")
            
            # --- JAVASCRIPT COPY COMPONENT ---
            # This replaces the broken st.copy_to_clipboard
            copy_text = st.session_state.last_result.replace("'", "\\'").replace("\n", "\\n")
            copy_js = f"""
                <button onclick="navigator.clipboard.writeText('{copy_text}'); alert('Copied to clipboard!')" 
                style="width: 100%; height: 45px; background: #00f2fe; border: none; border-radius: 12px; color: #050b1a; font-weight: bold; cursor: pointer; margin-bottom: 10px;">
                📋 Copy Result
                </button>
            """
            
            col1, col2 = st.columns(2)
            with col1:
                st.components.v1.html(copy_js, height=60)
            with col2:
                if st.button("🆕 New Chat"):
                    st.session_state.last_result = ""; st.rerun()
        else:
            st.title("🚀 Prompt Studio")
            prompt_input = st.text_area("What are we creating?", height=150)
            if st.button("GENERATE MASTERPIECE"):
                if prompt_input:
                    with st.spinner("Thinking..."):
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        response = model.generate_content(prompt_input)
                        st.session_state.last_result = response.text
                        st.session_state.usage_count += 1
                        
                        if st.session_state.user:
                            try:
                                supabase.postgrest.auth(st.session_state.access_token)
                                supabase.table("user_prompts").insert({
                                    "user_id": st.session_state.user.id,
                                    "input_text": prompt_input, "output_text": response.text
                                }).execute()
                            except: pass
                        st.rerun()

elif tab == 'My Library':
    st.title("📚 Library")
    if not st.session_state.user:
        st.info("Log in to see your collection.")
    else:
        try:
            supabase.postgrest.auth(st.session_state.access_token)
            data = supabase.table("user_prompts").select("*").order('created_at', desc=True).execute()
            if not data.data:
                st.write("Your library is empty.")
            else:
                for item in data.data:
                    with st.expander(f"📦 {item['input_text'][:50]}..."):
                        st.code(item['output_text'])
                        # Copy button inside expander
                        lib_copy_text = item['output_text'].replace("'", "\\'").replace("\n", "\\n")
                        lib_js = f"""<button onclick="navigator.clipboard.writeText('{lib_copy_text}');" style="background:#00f2fe; border:none; border-radius:5px; padding:5px 10px; cursor:pointer;">📋 Copy</button>"""
                        st.components.v1.html(lib_js, height=40)
        except Exception as e:
            st.error(f"Error: {e}")

st.markdown('</div>', unsafe_allow_html=True)
