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
    /* Smooth background and text */
    .stApp { 
        background: radial-gradient(circle at top right, #1e293b, #0f172a);
        color: #f8fafc;
        animation: fadeIn 1.5s ease-in-out;
    }
    
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

    /* Interactive Glass Box */
    .main-box { 
        background: rgba(255, 255, 255, 0.03); 
        backdrop-filter: blur(15px); 
        border-radius: 28px; 
        padding: 40px; 
        border: 1px solid rgba(255, 255, 255, 0.1); 
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .main-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 30px 60px -12px rgba(34, 211, 238, 0.2);
        border: 1px solid rgba(34, 211, 238, 0.3);
    }

    /* Input Glow */
    .stTextArea textarea { 
        background: rgba(15, 23, 42, 0.8) !important; 
        color: #22d3ee !important; 
        border: 1px solid rgba(34, 211, 238, 0.2) !important;
        border-radius: 16px !important;
    }
    .stTextArea textarea:focus { border-color: #22d3ee !important; }

    /* Neon Buttons */
    div.stButton > button { 
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%) !important;
        color: white !important; font-weight: 800 !important; 
        border-radius: 14px !important; border: none !important;
        transition: 0.4s all cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    div.stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 20px rgba(6, 182, 212, 0.6);
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
for key in ["user", "access_token", "usage_count", "last_result"]:
    if key not in st.session_state:
        st.session_state[key] = 0 if key == "usage_count" else None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("👤 Portal")
    if st.session_state.user:
        st.success(f"User: {st.session_state.user.email}")
        if st.button("Logout"): st.session_state.user = None; st.rerun()
    else:
        st.info(f"Free Credits: {st.session_state.usage_count}/3")
        mode = st.radio("Access", ["Login", "Sign Up"], horizontal=True)
        e = st.text_input("Email").strip()
        p = st.text_input("Password", type="password").strip()
        if st.button("Enter Studio"):
            try:
                res = supabase.auth.sign_in_with_password({"email": e, "password": p})
                st.session_state.user = res.user; st.session_state.access_token = res.session.access_token
                st.rerun()
            except: st.error("Login Failed")

# --- 5. HORIZONTAL NAVIGATION ---
# All three items are now on the same line
tab = sac.tabs([
    sac.TabsItem(label='Generator', icon='magic'),
    sac.TabsItem(label='Vault', icon='safe2'),
    sac.TabsItem(label='Guide', icon='book-half'),
], color='cyan', index=0, align='center')

current_tab = str(tab)

# --- 6. PAGE ROUTING ---
st.markdown('<div class="main-box">', unsafe_allow_html=True)

if current_tab == 'Generator':
    if not st.session_state.user and st.session_state.usage_count >= 3:
        st.warning("⚠️ Limit reached. Please Login.")
    else:
        if st.session_state.last_result:
            st.markdown("### 🔮 Result")
            st.code(st.session_state.last_result, language="markdown")
            # JavaScript Copy
            s_text = st.session_state.last_result.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "")
            copy_js = f"""<button onclick="navigator.clipboard.writeText(`{s_text}`).then(() => alert('Copied!'))" style="width: 100%; height: 50px; background: #22d3ee; border: none; border-radius: 14px; color: #0f172a; font-weight: 800; cursor: pointer;">📋 COPY TO CLIPBOARD</button>"""
            components.html(copy_js, height=60)
            if st.button("🆕 New Architect Job"): st.session_state.last_result = ""; st.rerun()
        else:
            st.title("Prompt Architect")
            p_input = st.text_area("Input your base idea...", height=200)
            if st.button("CONSTRUCT MASTERPIECE"):
                if p_input:
                    with st.spinner("Engineering..."):
                        try:
                            model = genai.GenerativeModel('gemini-2.5-flash')
                            logic = "Act as a Master Prompt Engineer. Rewrite this idea into a professional prompt with Persona, Task, Context, and Constraints: "
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
    if not st.session_state.user: st.info("🔐 Login to see your history.")
    else:
        try:
            supabase.postgrest.auth(st.session_state.access_token)
            data = supabase.table("user_prompts").select("*").order('created_at', desc=True).execute()
            for item in data.data:
                with st.expander(f"📁 {item['input_text'][:60]}..."):
                    st.code(item['output_text'])
        except: st.error("Vault access failed.")

elif current_tab == 'Guide':
    st.title("📖 Beginner Tutorial")
    st.write("Master the Prompt Architect in seconds.")
    c1, c2, c3 = st.columns(3)
    with c1: st.info("**1. Basic Idea**\nEnter a short phrase (e.g., 'Diet plan').")
    with c2: st.info("**2. AI Build**\nWe add professional constraints automatically.")
    with c3: st.info("**3. One Click**\nCopy and paste into ChatGPT or Gemini.")
    st.markdown("---")
    st.subheader("💡 Why use this?")
    st.write("Basic prompts give basic answers. Architect prompts give **professional results**.")

st.markdown('</div>', unsafe_allow_html=True)
