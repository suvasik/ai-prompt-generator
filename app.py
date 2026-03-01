import streamlit as st
import google.generativeai as genai
import streamlit_antd_components as sac
from supabase import create_client, Client

# --- 1. CONFIG & DB SETUP ---
st.set_page_config(page_title="Prompt Studio", page_icon="🪄", layout="wide")

# Connect to Secrets
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
except Exception as e:
    st.error("Missing Secrets! Ensure SUPABASE_URL, SUPABASE_KEY, and GEMINI_KEY are set.")

# --- 2. THE UI (Glassmorphism & Original Gradient) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        background-attachment: fixed;
    }
    .main-box {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 25px;
        padding: 40px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
    }
    div.stButton > button {
        background-color: #00f2fe !important;
        color: #050b1a !important;
        border-radius: 12px !important;
        font-weight: 900 !important;
        width: 100%;
        border: none !important;
    }
    h1, h2, h3, p, label, span { color: #ffffff !important; }
    .stTextArea textarea { background-color: rgba(255,255,255,0.1) !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "usage_count" not in st.session_state: st.session_state.usage_count = 0
if "user" not in st.session_state: st.session_state.user = None
if "last_result" not in st.session_state: st.session_state.last_result = ""

# --- 4. SIDEBAR AUTH (Sign Up & Login) ---
with st.sidebar:
    st.title("🔐 User Portal")
    if st.session_state.user:
        st.success(f"Logged in: {st.session_state.user.email}")
        if st.button("Log Out"):
            st.session_state.user = None
            st.rerun()
    else:
        auth_mode = st.radio("Mode", ["Login", "Sign Up"], horizontal=True)
        email_input = st.text_input("Email")
        pass_input = st.text_input("Password", type="password")
        
        # Strip spaces to prevent "Invalid Credentials" errors
        clean_email = email_input.strip()
        clean_pass = pass_input.strip()

        if auth_mode == "Login":
            if st.button("Sign In"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": clean_email, "password": clean_pass})
                    st.session_state.user = res.user
                    st.success("Login Successful!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Login Failed: Check if email is confirmed or password is correct.")
        else:
            if st.button("Create Account"):
                try:
                    res = supabase.auth.sign_up({"email": clean_email, "password": clean_pass})
                    st.success("Account Created! You can now switch to Login.")
                except Exception as e:
                    st.error(f"Sign Up Failed: {str(e)}")

# --- 5. MAIN NAVIGATION ---
menu_item = sac.tabs([
    sac.TabsItem(label='New Chat', icon='chat-square-dots-fill'),
    sac.TabsItem(label='History', icon='clock-fill'),
], align='center', variant='toggle', color='cyan')

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# --- 6. PAGE LOGIC ---
if menu_item == 'New Chat':
    # Limit check
    if not st.session_state.user and st.session_state.usage_count >= 3:
        st.warning("⚠️ Free limit reached (3/3). Please Login or Sign Up in the sidebar to continue.")
    else:
        if st.session_state.last_result:
            st.subheader("✨ Your Generated Prompt")
            st.code(st.session_state.last_result)
            c1, c2 = st.columns(2)
            if c1.button("🆕 New Chat"):
                st.session_state.last_result = ""; st.rerun()
            c2.download_button("📥 Download", st.session_state.last_result, "prompt.txt")
        else:
            u_input = st.text_area("Describe your idea...", height=150)
            if st.button("GENERATE MASTERPIECE"):
                if u_input:
                    # Using Gemini 2.5 Flash as per 2026 standards
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    resp = model.generate_content(u_input)
                    st.session_state.last_result = resp.text
                    st.session_state.usage_count += 1
                    
                    # Store in Supabase if logged in
                    if st.session_state.user:
                        try:
                            supabase.table("user_prompts").insert({
                                "user_id": st.session_state.user.id,
                                "input_text": u_input,
                                "output_text": resp.text
                            }).execute()
                        except:
                            st.error("Database connection error. History not saved.")
                    st.rerun()
                else:
                    st.error("Please enter a description first!")

elif menu_item == 'History':
    st.title("📜 History")
    if not st.session_state.user:
        st.info("Log in to see your permanent prompt history.")
    else:
        try:
            # Fetch user-specific history
            data = supabase.table("user_prompts").select("*").eq("user_id", st.session_state.user.id).order('created_at', descending=True).execute()
            if not data.data:
                st.write("No history found yet. Start chatting!")
            for item in data.data:
                with st.expander(f"Prompt: {item['input_text'][:40]}..."):
                    st.write(f"**Request:** {item['input_text']}")
                    st.code(item['output_text'])
        except Exception as e:
            st.error("Could not load history. Make sure your 'user_prompts' table exists.")

st.markdown('</div>', unsafe_allow_html=True)
