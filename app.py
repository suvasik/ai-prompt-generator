import streamlit as st
import google.generativeai as genai
import streamlit_antd_components as sac
from supabase import create_client, Client
import streamlit.components.v1 as components

# --- 1. CONFIG & DB SETUP ---
st.set_page_config(page_title="Prompt Studio Pro", page_icon="🪄", layout="wide")

# Removed @st.cache_resource to ensure a clean client every time
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    # Direct initialization is the most compatible across all library versions
    return create_client(url, key)

# Initialize clients
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
    }
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

# --- 4. SIDEBAR AUTH ---
with st.sidebar:
    st.title("👤 Account")
    
    if st.session_state.user:
        st.success(f"Logged in: {st.session_state.user.email}")
        if st.session_state.reset_mode:
            st.warning("⚠️ Set new password")
            new_pw = st.text_input("New Password", type="password")
            if st.button("Update Password"):
                try:
                    supabase.auth.update_user({"password": new_pw})
                    st.success("Updated! Log in again.")
                    st.session_state.user = None
                    st.session_state.reset_mode = False
                    st.rerun()
                except Exception as e: st.error(f"Error: {e}")
        
        if st.button("Logout"):
            st.session_state.user = None; st.session_state.access_token = None; st.rerun()
            
    elif st.session_state.reset_mode:
        st.subheader("🔑 Reset Password")
        email_reset = st.text_input("Email Address")
        if st.button("Send Reset Link"):
            try:
                supabase.auth.reset_password_for_email(email_reset)
                st.success("Link sent! Check your inbox.")
            except Exception as e: st.error(f"Error: {e}")
        if st.button("Back to Login"):
            st.session_state.reset_mode = False; st.rerun()

    else:
        st.write(f"Guest Usage: {st.session_state.usage_count}/3")
        st.progress(st.session_state.usage_count / 3)
        mode = st.radio("Mode", ["Login", "Sign Up"], horizontal=True)
        email = st.text_input("Email").strip()
        pw = st.text_input("Password", type="password").strip()
        
        if mode == "Login" and st.button("Sign In"):
            try:
                # Direct call to the fresh client
                res = supabase.auth.sign_in_with_password({"email": email, "password": pw})
                st.session_state.user = res.user
                st.session_state.access_token = res.session.access_token
                st.rerun()
            except Exception as e: st.error(f"Login failed: {e}")
            
        if mode == "Login" and st.button("❓ Forgot Password?"):
            st.session_state.reset_mode = True; st.rerun()
        
        if mode == "Sign Up" and st.button("Create Account"):
            try:
                supabase.auth.sign_up({"email": email, "password": pw})
                st.success("Success! Now Login.")
            except Exception as e: st.error(f"Error: {e}")

# --- 5. NAVIGATION (Updated with Guide) ---
try:
    tab = sac.tabs([
        sac.TabsItem(label='Architect', icon='cpu'),
        sac.TabsItem(label='Vault', icon='safe2'),
        sac.TabsItem(label='Guide', icon='book'), # New Tutorial Tab
    ], color='cyan', index=0)
except:
    tab_list = ['Architect', 'Vault', 'Guide']
    tab = st.tabs(tab_list)[0] 

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# --- 6. PAGE ROUTING ---
# ... (Keep Architect and Vault logic here) ...

if tab == 'Guide':
    st.title("📖 Beginner's Guide")
    st.write("Master the art of Prompt Engineering in 3 simple steps.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 1. The Idea 💡")
        st.caption("Start with a simple concept. Don't worry about details yet.")
        st.info("**Example:** 'Write a workout plan for a busy student.'")

    with col2:
        st.markdown("### 2. The Build 🏗️")
        st.caption("Click 'Construct Masterpiece'. Our AI wraps your idea in a professional framework.")
        st.info("**Logic:** We add Persona, Context, and strict Constraints automatically.")

    with col3:
        st.markdown("### 3. The Result 🚀")
        st.caption("Copy your engineered prompt and paste it into any AI (ChatGPT, Gemini, etc.).")
        st.info("**Success:** You get a 10x better answer than a basic question!")

    st.divider()
    st.subheader("💡 Pro-Tips for Better Results")
    st.markdown("""
    * **Be Specific:** Instead of 'Food', try 'Healthy keto dinner for two'.
    * **State the Format:** If you want a table, mention it in your idea!
    * **Use the Vault:** Login to save your best prompts forever.
    """)

# --- 6. PAGE ROUTING ---
if tab == 'Generator':
    if not st.session_state.user and st.session_state.usage_count >= 3:
        st.error("💡 Free limit reached. Please login!")
    else:
        if st.session_state.last_result:
            st.markdown("### ✨ AI Result")
            st.code(st.session_state.last_result, language="markdown")
            
            # Escape text for JS
            safe_text = st.session_state.last_result.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "")
            copy_button_html = f"""
                <button onclick="copyToClipboard()" style="width: 100%; height: 45px; background: linear-gradient(45deg, #00f2fe, #4facfe); border: none; border-radius: 12px; color: #050b1a; font-weight: bold; cursor: pointer; width:100%;">
                📋 Copy Result
                </button>
                <script>
                function copyToClipboard() {{
                    const text = `{safe_text}`;
                    navigator.clipboard.writeText(text).then(() => {{ alert('Copied!'); }});
                }}
                </script>
            """
            col1, col2 = st.columns(2)
            with col1: components.html(copy_button_html, height=70)
            with col2:
                if st.button("🆕 New Chat"):
                    st.session_state.last_result = ""; st.rerun()
        else:
            st.title("🚀 Prompt Studio")
            prompt_input = st.text_area("What are we creating?", height=150)
            if st.button("GENERATE MASTERPIECE"):
                if prompt_input:
                    with st.spinner("Thinking..."):
                        try:
                            model = genai.GenerativeModel('gemini-2.5-flash')
                            response = model.generate_content(prompt_input)
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
                            st.error(f"Error: {e}")

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
                        lib_safe_text = item['output_text'].replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "")
                        lib_copy_html = f"""
                            <button onclick="navigator.clipboard.writeText(`{lib_safe_text}`).then(() => alert('Copied!'))" 
                            style="background:#00f2fe; border:none; border-radius:8px; padding:8px 15px; cursor:pointer; font-weight:bold;">
                            📋 Copy
                            </button>
                        """
                        components.html(lib_copy_html, height=50)
        except Exception as e:
            st.error(f"History load failed: {e}")

st.markdown('</div>', unsafe_allow_html=True)
