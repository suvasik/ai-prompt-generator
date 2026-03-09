import streamlit as st
import google.generativeai as genai
import streamlit_antd_components as sac
from supabase import create_client
import streamlit.components.v1 as components

# --- 1. CONFIG & DB SETUP ---
st.set_page_config(page_title="Prompt Studio Pro", page_icon="🪄", layout="wide")

# Helper to initialize Supabase
def get_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error("Missing Supabase Secrets")
        return None

supabase = get_supabase()
genai.configure(api_key=st.secrets["GEMINI_KEY"])

# --- 2. ADVANCED UI & CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { 
        background: radial-gradient(circle at top right, #1e293b, #0f172a);
        color: #f8fafc;
    }
    .main-box { 
        background: rgba(255, 255, 255, 0.03); 
        backdrop-filter: blur(12px); 
        border-radius: 24px; 
        padding: 40px; 
        border: 1px solid rgba(255, 255, 255, 0.1); 
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }
    .stTextArea textarea { 
        background: rgba(15, 23, 42, 0.6) !important; 
        color: #22d3ee !important; 
        border: 1px solid rgba(34, 211, 238, 0.2) !important;
        border-radius: 16px !important;
    }
    div.stButton > button { 
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%) !important;
        color: white !important; font-weight: 700 !important; 
        border-radius: 12px !important; border: none !important;
        transition: 0.3s all ease !important;
    }
    div.stButton > button:hover { transform: translateY(-2px); filter: brightness(1.1); }
    h1, h2, h3 { 
        background: linear-gradient(to right, #22d3ee, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "user" not in st.session_state: st.session_state.user = None
if "access_token" not in st.session_state: st.session_state.access_token = None
if "usage_count" not in st.session_state: st.session_state.usage_count = 0
if "last_result" not in st.session_state: st.session_state.last_result = ""
if "reset_mode" not in st.session_state: st.session_state.reset_mode = False

# --- 4. SIDEBAR AUTH (Fixed SAC Logic) ---
with st.sidebar:
    st.markdown("### 🛡️ Access Portal")
    
    if st.session_state.user:
        st.success(f"Verified: {st.session_state.user.email}")
        if st.button("Secure Logout"):
            st.session_state.user = None; st.session_state.access_token = None; st.rerun()
    else:
        st.write(f"Credits: {st.session_state.usage_count}/3")
        st.progress(st.session_state.usage_count / 3)
        
        # Using a safer version of SAC Segmented to avoid TypeError
        try:
            mode = sac.segmented(
                items=[sac.SegmentedItem('Login'), sac.SegmentedItem('Register')],
                color='cyan', size='sm', align='center'
            )
        except:
            mode = st.radio("Access Mode", ["Login", "Register"], horizontal=True)

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
                st.success("Identity Created. Please Login.")
            except: st.error("Registration failed.")

# --- 5. NAVIGATION ---
tab = sac.tabs([
    sac.TabsItem(label='Architect', icon='cpu'),
    sac.TabsItem(label='Vault', icon='safe2'),
], align='center', variant='toggle', color='cyan')

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# --- 6. PAGE ROUTING ---
if tab == 'Architect':
    if not st.session_state.user and st.session_state.usage_count >= 3:
        st.warning("🚧 Locked: Authenticate for more generations.")
    else:
        if st.session_state.last_result:
            st.markdown("### 🔮 Optimized Prompt")
            st.code(st.session_state.last_result, language="markdown")
            
            # Escape text for JS
            safe_text = st.session_state.last_result.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "")
            copy_button_html = f"""
                <button onclick="copyToClipboard()" style="width: 100%; height: 50px; background: #22d3ee; border: none; border-radius: 12px; color: #0f172a; font-weight: 800; cursor: pointer;">
                📋 COPY TO CLIPBOARD
                </button>
                <script>
                function copyToClipboard() {{
                    const text = `{safe_text}`;
                    navigator.clipboard.writeText(text).then(() => {{ alert('Copied!'); }});
                }}
                </script>
            """
            c1, c2 = st.columns([3, 1])
            with c1: components.html(copy_button_html, height=70)
            with c2:
                if st.button("🆕 Clear"):
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
                        except Exception as e: st.error(f"Neural Error: {e}")

elif tab == 'Vault':
    st.title("🗄️ Secure Vault")
    if not st.session_state.user:
        st.info("🔐 The Vault is encrypted. Please log in.")
    else:
        try:
            supabase.postgrest.auth(st.session_state.access_token)
            data = supabase.table("user_prompts").select("*").order('created_at', desc=True).execute()
            for item in data.data:
                with st.expander(f"📁 {item['input_text'][:50]}..."):
                    st.code(item['output_text'])
        except Exception as e: st.error("Vault access failed.")

st.markdown('</div>', unsafe_allow_html=True)
