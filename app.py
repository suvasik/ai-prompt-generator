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
    except:
        return None

supabase = get_supabase()
genai.configure(api_key=st.secrets["GEMINI_KEY"])

# --- 2. ADVANCED UI & CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top right, #1e293b, #0f172a); color: #f8fafc; }
    .main-box { 
        background: rgba(255, 255, 255, 0.03); 
        backdrop-filter: blur(12px); 
        border-radius: 24px; 
        padding: 40px; 
        border: 1px solid rgba(255, 255, 255, 0.1); 
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }
    .stTextArea textarea { background: rgba(15, 23, 42, 0.6) !important; color: #22d3ee !important; border-radius: 16px !important; }
    div.stButton > button { 
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%) !important;
        color: white !important; font-weight: 700 !important; border-radius: 12px !important; border: none !important;
    }
    h1, h2, h3 { background: linear-gradient(to right, #22d3ee, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
for key in ["user", "access_token", "usage_count", "last_result"]:
    if key not in st.session_state:
        st.session_state[key] = 0 if key == "usage_count" else None

# --- 4. SIDEBAR AUTH ---
with st.sidebar:
    st.title("🛡️ Access Portal")
    if st.session_state.user:
        st.success(f"User: {st.session_state.user.email}")
        if st.button("Logout"):
            st.session_state.user = None; st.rerun()
    else:
        st.write(f"Credits: {st.session_state.usage_count}/3")
        # Standard Streamlit radio is safer for Auth toggles
        mode = st.radio("Account", ["Login", "Register"], horizontal=True)
        email = st.text_input("Email").strip()
        pw = st.text_input("Password", type="password").strip()
        
        if mode == "Login" and st.button("Enter Studio"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": pw})
                st.session_state.user = res.user
                st.session_state.access_token = res.session.access_token
                st.rerun()
            except: st.error("Access Denied.")
        
        if mode == "Register" and st.button("Create Account"):
            try:
                supabase.auth.sign_up({"email": email, "password": pw})
                st.success("Account Created! Please Login.")
            except: st.error("Sign up failed.")

# --- 5. NAVIGATION (Fixed Compatibility) ---
# We use a try-except block here to handle SAC version differences
try:
    tab = sac.tabs([
        sac.TabsItem(label='Architect', icon='cpu'),
        sac.TabsItem(label='Vault', icon='safe2'),
    ], color='cyan', index=0)
except:
    # Fallback to standard Streamlit tabs if SAC fails
    tab_list = ["Architect", "Vault"]
    st_tabs = st.tabs(tab_list)
    tab = tab_list[0] # Default for simpler logic

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# --- 6. ARCHITECT PAGE ---
if tab == 'Architect' or (isinstance(tab, str) and tab == 'Architect'):
    if not st.session_state.user and st.session_state.usage_count >= 3:
        st.warning("🚧 Locked: Please login for more credits.")
    else:
        if st.session_state.last_result:
            st.markdown("### 🔮 Optimized Prompt")
            st.code(st.session_state.last_result, language="markdown")
            
            safe_text = st.session_state.last_result.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "")
            copy_html = f"""
                <button onclick="navigator.clipboard.writeText(`{safe_text}`).then(() => alert('Copied!'))" 
                style="width: 100%; height: 50px; background: #22d3ee; border: none; border-radius: 12px; color: #0f172a; font-weight: 800; cursor: pointer;">
                📋 COPY TO CLIPBOARD
                </button>
            """
            components.html(copy_html, height=60)
            if st.button("🆕 New Prompt"):
                st.session_state.last_result = ""; st.rerun()
        else:
            st.title("🪄 Prompt Architect")
            prompt_input = st.text_area("Input your base concept...", height=200)
            
            if st.button("CONSTRUCT MASTER PROMPT"):
                if prompt_input:
                    with st.spinner("Engineering..."):
                        try:
                            model = genai.GenerativeModel('gemini-2.5-flash')
                            # Choice B: Structured Prompt Engineering Logic
                            sys_logic = "Act as a Master Prompt Engineer. Rewrite this idea into a professional prompt with Persona, Task, Context, and Constraints: "
                            response = model.generate_content(sys_logic + prompt_input)
                            
                            st.session_state.last_result = response.text
                            st.session_state.usage_count += 1
                            
                            if st.session_state.user:
                                supabase.postgrest.auth(st.session_state.access_token)
                                supabase.table("user_prompts").insert({
                                    "user_id": st.session_state.user.id,
                                    "input_text": prompt_input, "output_text": response.text
                                }).execute()
                            st.rerun()
                        except Exception as e: st.error(f"AI Link Error: {e}")

# --- 7. VAULT PAGE ---
elif tab == 'Vault' or (isinstance(tab, str) and tab == 'Vault'):
    st.title("🗄️ Secure Vault")
    if not st.session_state.user:
        st.info("🔐 Please log in to view your history.")
    else:
        try:
            supabase.postgrest.auth(st.session_state.access_token)
            data = supabase.table("user_prompts").select("*").order('created_at', desc=True).execute()
            if not data.data:
                st.write("Vault is empty.")
            else:
                for item in data.data:
                    with st.expander(f"📁 {item['input_text'][:50]}..."):
                        st.code(item['output_text'])
        except Exception as e: st.error(f"Vault error: {e}")

st.markdown('</div>', unsafe_allow_html=True)
