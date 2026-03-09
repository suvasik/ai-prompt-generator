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
    /* Main Background */
    .stApp { 
        background: radial-gradient(circle at top right, #1e293b, #0f172a);
        color: #f8fafc;
    }
    
    /* Glassmorphism Card */
    .main-box { 
        background: rgba(255, 255, 255, 0.03); 
        backdrop-filter: blur(12px); 
        border-radius: 24px; 
        padding: 40px; 
        border: 1px solid rgba(255, 255, 255, 0.1); 
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        margin-top: 20px;
    }

    /* Input Styling */
    .stTextArea textarea { 
        background: rgba(15, 23, 42, 0.6) !important; 
        color: #22d3ee !important; 
        border: 1px solid rgba(34, 211, 238, 0.2) !important;
        border-radius: 16px !important;
        transition: all 0.3s ease;
    }
    .stTextArea textarea:focus {
        border-color: #22d3ee !important;
        box-shadow: 0 0 15px rgba(34, 211, 238, 0.1) !important;
    }

    /* Buttons */
    div.stButton > button { 
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%) !important;
        color: white !important; 
        font-weight: 700 !important; 
        border-radius: 12px !important; 
        border: none !important;
        padding: 12px 24px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px -5px rgba(6, 182, 212, 0.5);
        filter: brightness(1.1);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Headers */
    h1, h2, h3 { 
        font-family: 'Inter', sans-serif;
        background: linear-gradient(to right, #22d3ee, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    
    /* Code Block Styling */
    code { color: #818cf8 !important; }
    div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
for key in ["user", "access_token", "usage_count", "last_result", "reset_mode"]:
    if key not in st.session_state:
        st.session_state[key] = 0 if key == "usage_count" else (False if key == "reset_mode" else None)

# --- 4. SIDEBAR AUTH ---
with st.sidebar:
    st.markdown("### 🛡️ Portal Control")
    
    if st.session_state.user:
        st.success(f"Verified: {st.session_state.user.email}")
        if st.session_state.reset_mode:
            st.warning("🔄 Security Update Required")
            new_pw = st.text_input("New Password", type="password")
            if st.button("Update Keys"):
                try:
                    supabase.auth.update_user({"password": new_pw})
                    st.success("Success! Redirecting...")
                    st.session_state.user = None
                    st.session_state.reset_mode = False
                    st.rerun()
                except Exception as e: st.error(f"Error: {e}")
        
        if st.button("Secure Logout"):
            st.session_state.user = None; st.session_state.access_token = None; st.rerun()
            
    elif st.session_state.reset_mode:
        st.subheader("🔑 Recovery")
        email_reset = st.text_input("Recovery Email")
        if st.button("Send Magic Link"):
            try:
                supabase.auth.reset_password_for_email(email_reset)
                st.info("Check your inbox!")
            except Exception as e: st.error(f"Error: {e}")
        if st.button("Back to Login"):
            st.session_state.reset_mode = False; st.rerun()

    else:
        st.write(f"Free Credits: {st.session_state.usage_count}/3")
        st.progress(st.session_state.usage_count / 3)
        mode = sac.segmented(
            items=[sac.SegmentedItem(label='Login'), sac.SegmentedItem(label='Register')],
            align='center', variant='outline', color='cyan', size='sm'
        )
        email = st.text_input("Email").strip()
        pw = st.text_input("Password", type="password").strip()
        
        if mode == "Login" and st.button("Enter Studio"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": pw})
                st.session_state.user = res.user
                st.session_state.access_token = res.session.access_token
                st.rerun()
            except Exception as e: st.error("Access Denied.")
            
        if mode == "Login" and st.button("Forgot Access?"):
            st.session_state.reset_mode = True; st.rerun()
        
        if mode == "Register" and st.button("Create ID"):
            try:
                supabase.auth.sign_up({"email": email, "password": pw})
                st.success("Identity Created. Please Login.")
            except Exception as e: st.error("Registration failed.")

# --- 5. NAVIGATION ---
tab = sac.tabs([
    sac.TabsItem(label='Architect', icon='cpu'),
    sac.TabsItem(label='Vault', icon='safe2'),
], align='center', variant='toggle', color='cyan')

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# --- 6. PAGE ROUTING ---
if tab == 'Architect':
    if not st.session_state.user and st.session_state.usage_count >= 3:
        st.warning("🚧 System Locked: Please authenticate to continue generating.")
    else:
        if st.session_state.last_result:
            st.markdown("### 🔮 Optimized Intelligence")
            st.code(st.session_state.last_result, language="markdown")
            
            # Escape text for JS
            safe_text = st.session_state.last_result.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "")
            copy_button_html = f"""
                <button onclick="copyToClipboard()" style="width: 100%; height: 50px; background: #22d3ee; border: none; border-radius: 12px; color: #0f172a; font-weight: 800; cursor: pointer; transition: 0.3s; font-family: sans-serif;">
                📋 COPY TO CLIPBOARD
                </button>
                <script>
                function copyToClipboard() {{
                    const text = `{safe_text}`;
                    navigator.clipboard.writeText(text).then(() => {{ alert('Copied to Clipboard!'); }});
                }}
                </script>
            """
            c1, c2 = st.columns([3, 1])
            with c1: components.html(copy_button_html, height=70)
            with c2:
                if st.button("🆕 Reset"):
                    st.session_state.last_result = ""; st.rerun()
        else:
            st.title("🪄 Prompt Architect")
            st.write("Convert vague ideas into high-performance professional prompts.")
            prompt_input = st.text_area("Input your base concept...", height=200, placeholder="e.g., A comprehensive marketing strategy for a sustainable fashion brand...")
            
            if st.button("CONSTRUCT PROMPT"):
                if prompt_input:
                    with st.spinner("Analyzing & Expanding..."):
                        try:
                            # Added a system-level nudge for better prompts
                            model = genai.GenerativeModel('gemini-2.5-flash')
                            enriched_query = f"Act as a Master Prompt Engineer. Refine and expand the following idea into a professional, structured prompt: {prompt_input}"
                            response = model.generate_content(enriched_query)
                            st.session_state.last_result = response.text
                            st.session_state.usage_count += 1
                            
                            if st.session_state.user:
                                supabase.postgrest.auth(st.session_state.access_token)
                                supabase.table("user_prompts").insert({
                                    "user_id": st.session_state.user.id,
                                    "input_text": prompt_input, "output_text": response.text
                                }).execute()
                            st.rerun()
                        except Exception as e:
                            st.error("Neural link interrupted. Try again.")

elif tab == 'Vault':
    st.title("🗄️ Secure Vault")
    if not st.session_state.user:
        st.info("🔐 The Vault is encrypted. Please log in to view saved prompts.")
    else:
        try:
            supabase.postgrest.auth(st.session_state.access_token)
            data = supabase.table("user_prompts").select("*").order('created_at', desc=True).execute()
            if not data.data:
                st.write("Vault is currently empty.")
            else:
                for item in data.data:
                    with st.expander(f"📁 {item['input_text'][:60]}..."):
                        st.markdown("**Engineered Output:**")
                        st.code(item['output_text'])
                        l_safe = item['output_text'].replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "")
                        l_copy = f"""<button onclick="navigator.clipboard.writeText(`{l_safe}`).then(() => alert('Prompt Copied!'))" style="background:#22d3ee; border:none; border-radius:8px; padding:10px 20px; cursor:pointer; font-weight:bold; color:#0f172a;">📋 Copy Prompt</button>"""
                        components.html(l_copy, height=50)
        except Exception as e:
            st.error("Vault access failed.")

st.markdown('</div>', unsafe_allow_html=True)
