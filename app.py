import streamlit as st
import google.generativeai as genai
import streamlit_antd_components as sac
from supabase import create_client, Client
import streamlit.components.v1 as components

# --- 1. CONFIG & DB SETUP ---
st.set_page_config(page_title="Prompt Studio Pro", page_icon="🪄", layout="wide")

# We define this globally to ensure all functions can see it
def get_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        # Basic initialization is most compatible with Streamlit Cloud environments
        return create_client(url, key)
    except Exception as e:
        st.error(f"Supabase Setup Error: {e}")
        return None

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
    div.stButton > button { 
        background: linear-gradient(45deg, #00f2fe, #4facfe) !important;
        color: #050b1a !important; font-weight: 800 !important; 
        border-radius: 12px !important; border: none !important;
        transition: 0.3s all ease;
    }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0, 242, 254, 0.4); }
    h1, h2, h3, p, span, label { color: white !important; }
    .stTextArea textarea { background-color: rgba(0,0,0,0.2) !important; color: #00f2fe !important; border-radius: 12px !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "user" not in st.session_state: st.session_state.user = None
if "access_token" not in st.session_state: st.session_state.access_token = None
if "usage_count" not in st.session_state: st.session_state.usage_count = 0
if "last_result" not in st.session_state: st.session_state.last_result = ""
if "reset_mode" not in st.session_state: st.session_state.reset_mode = False

# --- 4. SIDEBAR AUTH & RECOVERY ---
with st.sidebar:
    st.title("👤 Account")
    
    if st.session_state.user:
        st.success(f"Logged in: {st.session_state.user.email}")
        
        # Check for Password Recovery State
        if st.session_state.reset_mode:
            st.warning("🔄 Security: Update Password")
            new_pw = st.text_input("New Password", type="password")
            if st.button("Confirm Update"):
                try:
                    supabase.auth.update_user({"password": new_pw})
                    st.success("Password Updated! Logging out...")
                    st.session_state.user = None
                    st.session_state.reset_mode = False
                    st.rerun()
                except Exception as e: st.error(f"Update failed: {e}")
        
        if st.button("Logout"):
            st.session_state.user = None; st.session_state.access_token = None; st.rerun()
            
    elif st.session_state.reset_mode:
        st.subheader("🔑 Reset Password")
        email_reset = st.text_input("Enter Email")
        if st.button("Send Reset Email"):
            try:
                supabase.auth.reset_password_for_email(email_reset)
                st.info("Check your inbox for the link!")
            except Exception as e: st.error(f"Error: {e}")
        if st.button("Back to Login"):
            st.session_state.reset_mode = False; st.rerun()

    else:
        st.write(f"Guest Usage: {st.session_state.usage_count}/3")
        st.progress(st.session_state.usage_count / 3)
        mode = st.radio("Access", ["Login", "Sign Up"], horizontal=True)
        email = st.text_input("Email").strip()
        pw = st.text_input("Password", type="password").strip()
        
        if mode == "Login" and st.button("Sign In"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": pw})
                st.session_state.user = res.user
                st.session_state.access_token = res.session.access_token
                st.rerun()
            except: st.error("Login failed. Check internet/credentials.")
            
        if mode == "Login" and st.button("❓ Forgot Password?"):
            st.session_state.reset_mode = True; st.rerun()
        
        if mode == "Sign Up" and st.button("Create Account"):
            try:
                supabase.auth.sign_up({"email": email, "password": pw})
                st.success("Account Created! You can now login.")
            except Exception as e: st.error(f"Sign up error: {e}")

# --- 5. NAVIGATION TABS ---
tab = sac.tabs([
    sac.TabsItem(label='Generator', icon='magic'),
    sac.TabsItem(label='My Library', icon='folder2-open'),
], align='center', variant='toggle', color='cyan')

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# --- 6. GENERATOR PAGE ---
if tab == 'Generator':
    if not st.session_state.user and st.session_state.usage_count >= 3:
        st.error("💡 Daily limit reached. Please log in for unlimited access.")
    else:
        if st.session_state.last_result:
            st.markdown("### ✨ AI Masterpiece")
            st.code(st.session_state.last_result, language="markdown")
            
            # Bulletproof JS Copy Button
            safe_text = st.session_state.last_result.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "")
            copy_js = f"""
                <button onclick="copyToClipboard()" style="width: 100%; height: 45px; background: linear-gradient(45deg, #00f2fe, #4facfe); border: none; border-radius: 12px; color: #050b1a; font-weight: bold; cursor: pointer; font-family: sans-serif;">
                📋 Copy to Clipboard
                </button>
                <script>
                function copyToClipboard() {{
                    const text = `{safe_text}`;
                    navigator.clipboard.writeText(text).then(() => {{ alert('Text Copied!'); }});
                }}
                </script>
            """
            c1, c2 = st.columns(2)
            with c1: components.html(copy_js, height=70)
            with c2:
                if st.button("🆕 Clear & Restart"):
                    st.session_state.last_result = ""; st.rerun()
        else:
            st.title("🚀 Prompt Studio")
            prompt_input = st.text_area("What are you building today?", height=150, placeholder="e.g., Create a 5-day itinerary for Tokyo...")
            if st.button("GENERATE"):
                if prompt_input:
                    with st.spinner("Connecting to Gemini AI..."):
                        try:
                            model = genai.GenerativeModel('gemini-2.5-flash')
                            response = model.generate_content(prompt_input)
                            st.session_state.last_result = response.text
                            st.session_state.usage_count += 1
                            
                            # Log to Supabase if logged in
                            if st.session_state.user:
                                try:
                                    supabase.postgrest.auth(st.session_state.access_token)
                                    supabase.table("user_prompts").insert({
                                        "user_id": st.session_state.user.id,
                                        "input_text": prompt_input, 
                                        "output_text": response.text
                                    }).execute()
                                except: pass
                            st.rerun()
                        except Exception as e:
                            st.error(f"AI Timeout: {e}")

# --- 7. LIBRARY PAGE ---
elif tab == 'My Library':
    st.title("📚 Your Prompt History")
    if not st.session_state.user:
        st.info("Your history is saved locally for this session. Log in to save it permanently in the cloud.")
    else:
        try:
            supabase.postgrest.auth(st.session_state.access_token)
            data = supabase.table("user_prompts").select("*").order('created_at', desc=True).execute()
            if not data.data:
                st.write("Your cloud library is empty.")
            else:
                for item in data.data:
                    with st.expander(f"📦 {item['input_text'][:60]}..."):
                        st.write(f"**Prompt:** {item['input_text']}")
                        st.code(item['output_text'])
                        # Copy inside expander
                        lib_safe = item['output_text'].replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "")
                        lib_copy_html = f"""<button onclick="navigator.clipboard.writeText(`{lib_safe}`).then(() => alert('Copied!'))" style="background:#00f2fe; border:none; border-radius:8px; padding:8px 15px; cursor:pointer; font-weight:bold;">📋 Copy</button>"""
                        components.html(lib_copy_html, height=50)
        except Exception as e:
            st.error(f"Library sync error: {e}")

st.markdown('</div>', unsafe_allow_html=True)
