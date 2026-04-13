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

# --- 2. HIGH-INTERACTION UI & CSS ---
st.markdown("""
    <style>
    .stApp { 
        background: radial-gradient(circle at top right, #1e293b, #0f172a);
        color: #f8fafc;
        animation: fadeIn 1.2s ease-in-out;
    }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

    .main-box { 
        background: rgba(255, 255, 255, 0.03); 
        backdrop-filter: blur(20px); 
        border-radius: 28px; 
        padding: 40px; 
        border: 1px solid rgba(255, 255, 255, 0.1); 
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
        transition: all 0.3s ease;
    }
    .main-box:hover {
        border: 1px solid rgba(34, 211, 238, 0.4);
        box-shadow: 0 30px 60px -12px rgba(34, 211, 238, 0.15);
    }

    .stTextArea textarea { 
        background: rgba(15, 23, 42, 0.8) !important; 
        color: #22d3ee !important; 
        border: 1px solid rgba(34, 211, 238, 0.2) !important;
        border-radius: 16px !important;
    }

    div.stButton > button { 
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%) !important;
        color: white !important; font-weight: 800 !important; 
        border-radius: 14px !important; border: none !important;
        transition: 0.3s all ease !important;
    }
    div.stButton > button:hover { transform: scale(1.02); filter: brightness(1.1); }
    
    h1, h2, h3 { 
        background: linear-gradient(90deg, #22d3ee, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
for key in ["user", "access_token", "usage_count", "last_result"]:
    if key not in st.session_state:
        st.session_state[key] = 0 if key == "usage_count" else None

# --- 4. SIDEBAR AUTH ---
with st.sidebar:
    st.title("👤 Portal")
    if st.session_state.user:
        st.success(f"Verified: {st.session_state.user.email}")
        if st.button("Logout"): 
            st.session_state.user = None
            st.session_state.access_token = None
            st.rerun()
    else:
        st.write(f"Credits: {st.session_state.usage_count}/3")
        st.progress(st.session_state.usage_count / 3)
        mode = st.radio("Access", ["Login", "Sign Up"], horizontal=True)
        email = st.text_input("Email").strip()
        pw = st.text_input("Password", type="password").strip()
        if st.button("Enter Studio"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": pw})
                st.session_state.user = res.user
                st.session_state.access_token = res.session.access_token
                st.rerun()
            except: st.error("Login Failed")

# --- 5. HORIZONTAL NAVIGATION ---
tab = sac.tabs([
    sac.TabsItem(label='Generator', icon='magic'),
    sac.TabsItem(label='Vault', icon='safe2'),
    sac.TabsItem(label='Guide', icon='book-half'),
], color='cyan', index=0, align='center')

current_tab = str(tab)

# --- 6. PAGE ROUTING ---
st.markdown('<div class="main-box">', unsafe_allow_html=True)

if current_tab == 'Generator':
    with st.expander("📖 Beginner's Guide: How to use Prompt Architect"):
        c1, c2, c3 = st.columns(3)
        with c1: st.info("**1. Idea:** Enter a simple concept.")
        with c2: st.info("**2. Build:** AI adds professional structure.")
        with c3: st.info("**3. Copy:** Use the result in ChatGPT/Gemini.")

    if not st.session_state.user and st.session_state.usage_count >= 3:
        st.warning("🚧 Locked: Please login to save your masterpieces.")
    else:
        if st.session_state.last_result:
            st.markdown("### 🔮 Engineered Prompt")
            st.code(st.session_state.last_result, language="markdown")
            
            # Button to clear and start over
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🆕 New Architect Job", use_container_width=True):
                    st.session_state.last_result = ""
                    st.rerun()
        else:
            st.title("🏗️ Prompt Architect")
            p_input = st.text_area("Input your base idea...", height=200, placeholder="e.g. A Python script for data analysis")
            if st.button("CONSTRUCT MASTERPIECE"):
                if p_input:
                    with st.spinner("Engineering..."):
                        try:
                            model = genai.GenerativeModel('gemini-2.5-flash')
                            logic = "Act as a Master Prompt Engineer. Rewrite this into a professional prompt with Persona, Task, Context, and Constraints: "
                            response = model.generate_content(logic + p_input)
                            st.session_state.last_result = response.text
                            st.session_state.usage_count += 1
                            if st.session_state.user:
                                supabase.postgrest.auth(st.session_state.access_token)
                                supabase.table("user_prompts").insert({"user_id": st.session_state.user.id, "input_text": p_input, "output_text": response.text}).execute()
                            st.rerun()
                        except Exception as e: st.error(f"Error: {e}")

elif current_tab == 'Vault':
    st.title("🗄️ Secure Vault")
    if not st.session_state.user:
        st.info("🔐 The Vault is encrypted. Please login.")
    else:
        try:
            supabase.postgrest.auth(st.session_state.access_token)
            data = supabase.table("user_prompts").select("*").order('created_at', desc=True).execute()
            if not data.data:
                st.write("Vault is empty.")
            else:
                for item in data.data:
                    with st.expander(f"📁 {item['input_text'][:60]}..."):
                        st.code(item['output_text'])
        except: st.error("Vault access failed.")

elif current_tab == 'Guide':
    st.title("📖 Beginner Tutorial")
    st.write("Turn your 5-word idea into a 5-star prompt.")
    c1, c2, c3 = st.columns(3)
    with c1: st.info("**1. Idea**\nEnter a basic concept (e.g. 'Fitness plan').")
    with c2: st.info("**2. Build**\nAI adds professional constraints automatically.")
    with c3: st.info("**3. One Click**\nCopy directly from the code block above.")
    st.divider()
    st.subheader("💡 Why this is better?")
    st.markdown("""
    * **Structure:** We use the **RTF Framework** (Role-Task-Format).
    * **Precision:** Professional prompts reduce AI 'hallucinations'.
    * **Persistence:** Save your best engineering work in the Vault.
    """)

st.markdown('</div>', unsafe_allow_html=True)
