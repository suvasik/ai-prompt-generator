import streamlit as st
import google.generativeai as genai
import streamlit_antd_components as sac
from supabase import create_client, Client
import streamlit.components.v1 as components

# --- 1. CONFIG & DB SETUP ---
st.set_page_config(page_title="Prompt Studio Pro", page_icon="🪄", layout="wide")

def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()
genai.configure(api_key=st.secrets["GEMINI_KEY"])

# --- 2. ADVANCED UI & CUSTOM CSS ---
st.markdown("""
    <style>
    /* Main Background with Deep Gradient */
    .stApp { 
        background: radial-gradient(circle at top right, #1e293b, #0f172a);
        color: #f8fafc;
    }
    
    /* Modern Glassmorphism Container */
    .main-box { 
        background: rgba(255, 255, 255, 0.03); 
        backdrop-filter: blur(15px); 
        border-radius: 28px; 
        padding: 40px; 
        border: 1px solid rgba(255, 255, 255, 0.1); 
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
        margin-top: 20px;
    }

    /* Input Field Styling */
    .stTextArea textarea { 
        background: rgba(15, 23, 42, 0.6) !important; 
        color: #22d3ee !important; 
        border: 1px solid rgba(34, 211, 238, 0.2) !important;
        border-radius: 16px !important;
        font-size: 1.1rem !important;
    }

    /* High-Gloss Buttons */
    div.stButton > button { 
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%) !important;
        color: white !important; 
        font-weight: 800 !important; 
        border-radius: 14px !important; 
        border: none !important;
        padding: 12px 28px !important;
        transition: 0.4s all cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div.stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 24px rgba(6, 182, 212, 0.4);
        filter: brightness(1.2);
    }

    /* Custom Header Gradients */
    h1, h2, h3 { 
        background: linear-gradient(90deg, #22d3ee, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
for key in ["user", "access_token", "usage_count", "last_result", "reset_mode"]:
    if key not in st.session_state:
        st.session_state[key] = 0 if key == "usage_count" else (False if key == "reset_mode" else None)

# --- 4. SIDEBAR AUTH ---
with st.sidebar:
    st.markdown("### 👤 Studio Access")
    if st.session_state.user:
        st.success(f"Verified: {st.session_state.user.email}")
        if st.button("Logout"):
            st.session_state.user = None; st.rerun()
    else:
        st.write(f"Free Credits: {st.session_state.usage_count}/3")
        st.progress(st.session_state.usage_count / 3)
        # Using a safer radio toggle for auth to avoid library crashes
        mode = st.radio("Portal Mode", ["Login", "Sign Up"], horizontal=True)
        email = st.text_input("Email")
        pw = st.text_input("Password", type="password")
        
        if st.button("Enter Studio"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": pw})
                st.session_state.user = res.user
                st.session_state.access_token = res.session.access_token
                st.rerun()
            except: st.error("Access Denied.")

# --- 5. NAVIGATION (Bulletproof SAC Logic) ---
# Wrapping the SAC Tabs in a try-except to prevent the TypeError
try:
    tab = sac.tabs([
        sac.TabsItem(label='Generator', icon='magic'),
        sac.TabsItem(label='My Library', icon='folder2-open'),
    ], color='cyan', index=0) # Removed 'align' and 'variant' which usually cause the error
except:
    # Fallback to standard Streamlit tabs if the library fails
    tab_list = ['Generator', 'My Library']
    st_tabs = st.tabs(tab_list)
    tab = tab_list[0] 

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# --- 6. PAGE ROUTING ---
if tab == 'Generator':
    if not st.session_state.user and st.session_state.usage_count >= 3:
        st.warning("🚧 Credit limit reached. Please login to save your masterpieces.")
    else:
        if st.session_state.last_result:
            st.markdown("### 🔮 Optimized Prompt")
            st.code(st.session_state.last_result, language="markdown")
            
            # Professional JS Copy Utility
            s_text = st.session_state.last_result.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "")
            copy_js = f"""
                <button onclick="navigator.clipboard.writeText(`{s_text}`).then(() => alert('Copied to Clipboard!'))" 
                style="width: 100%; height: 50px; background: #22d3ee; border: none; border-radius: 14px; color: #0f172a; font-weight: 800; cursor: pointer; transition: 0.3s;">
                📋 COPY RESULT
                </button>
            """
            c1, c2 = st.columns([3, 1])
            with c1: components.html(copy_js, height=70)
            with c2: 
                if st.button("🆕 Reset"):
                    st.session_state.last_result = ""; st.rerun()
        else:
            st.title("🏗️ Prompt Architect")
            st.write("Convert vague ideas into high-performance professional instructions.")
            p_input = st.text_area("What should the AI do for you?", height=200, placeholder="e.g. Write a fitness plan for a vegetarian marathon runner...")
            
            if st.button("GENERATE MASTERPIECE"):
                if p_input:
                    with st.spinner("Engineering Professional Prompt..."):
                        try:
                            # Implementing Choice B: The Prompt Architect Logic
                            model = genai.GenerativeModel('gemini-2.5-flash')
                            # We wrap the user input in a "System Frame" to force the AI to act as a Prompt Engineer
                            system_instruction = "Act as a Master Prompt Engineer. Refine the following user idea into a professional, structured prompt including Persona, Context, Task, and Constraints: "
                            response = model.generate_content(system_instruction + p_input)
                            
                            st.session_state.last_result = response.text
                            st.session_state.usage_count += 1
                            
                            if st.session_state.user:
                                supabase.postgrest.auth(st.session_state.access_token)
                                supabase.table("user_prompts").insert({
                                    "user_id": st.session_state.user.id,
                                    "input_text": p_input, "output_text": response.text
                                }).execute()
                            st.rerun()
                        except Exception as e: st.error("AI Neural link lost. Try again.")

elif tab == 'My Library':
    st.title("🗄️ Secure Vault")
    if not st.session_state.user:
        st.info("🔐 The Vault is encrypted. Please log in to view your history.")
    else:
        try:
            supabase.postgrest.auth(st.session_state.access_token)
            data = supabase.table("user_prompts").select("*").order('created_at', desc=True).execute()
            if not data.data:
                st.write("The vault is currently empty.")
            else:
                for item in data.data:
                    with st.expander(f"📁 {item['input_text'][:60]}..."):
                        st.code(item['output_text'])
                        # Copy button for library items
                        l_text = item['output_text'].replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "")
                        l_copy = f"""<button onclick="navigator.clipboard.writeText(`{l_text}`).then(() => alert('Copied!'))" style="background:#22d3ee; border:none; border-radius:8px; padding:10px 20px; cursor:pointer; font-weight:bold; color:#0f172a;">📋 Copy</button>"""
                        components.html(l_copy, height=50)
        except: st.error("Vault access failed.")

st.markdown('</div>', unsafe_allow_html=True)
