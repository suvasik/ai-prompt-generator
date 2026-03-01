import streamlit as st
import google.generativeai as genai
import streamlit_antd_components as sac
from supabase import create_client, Client

# --- 1. CONFIG & DB SETUP ---
st.set_page_config(page_title="Prompt Studio Pro", page_icon="🪄", layout="wide")

# Initialize Connections
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
except Exception as e:
    st.error("Missing Secrets! Ensure SUPABASE_URL, SUPABASE_KEY, and GEMINI_KEY are in Streamlit Cloud.")

# --- 2. THE UI (Original Gradient + Glassmorphism) ---
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
        transition: 0.3s;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 15px #00f2fe;
    }
    h1, h2, h3, p, label, span { color: #ffffff !important; }
    .stTextArea textarea { background-color: rgba(255,255,255,0.1) !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "usage_count" not in st.session_state: st.session_state.usage_count = 0
if "user" not in st.session_state: st.session_state.user = None
if "last_result" not in st.session_state: st.session_state.last_result = ""

# --- 4. SIDEBAR AUTH ---
with st.sidebar:
    st.title("🔐 Access Portal")
    if st.session_state.user:
        st.success(f"Logged in as: \n{st.session_state.user.email}")
        if st.button("Log Out"):
            st.session_state.user = None
            st.rerun()
    else:
        auth_mode = st.radio("Choose Action", ["Login", "Sign Up"], horizontal=True)
        email_in = st.text_input("Email").strip()
        pass_in = st.text_input("Password", type="password").strip()

        if auth_mode == "Login":
            if st.button("Sign In"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email_in, "password": pass_in})
                    st.session_state.user = res.user
                    st.rerun()
                except Exception as e:
                    st.error("Login Failed. Check if email is confirmed in Supabase.")
        else:
            if st.button("Create Account"):
                try:
                    supabase.auth.sign_up({"email": email_in, "password": pass_in})
                    st.success("Account created! Now switch to 'Login'.")
                except Exception as e:
                    st.error(f"Sign Up Error: {e}")

# --- 5. NAVIGATION ---
menu_item = sac.tabs([
    sac.TabsItem(label='New Chat', icon='chat-square-dots-fill'),
    sac.TabsItem(label='History', icon='clock-fill'),
], align='center', variant='toggle', color='cyan')

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# --- 6. APP LOGIC ---
if menu_item == 'New Chat':
    # Limit check for Guests
    if not st.session_state.user and st.session_state.usage_count >= 3:
        st.warning("🚀 You've used your 3 free prompts! Please Login to continue.")
    else:
        if st.session_state.last_result:
            st.subheader("✨ Generated Result")
            st.code(st.session_state.last_result)
            c1, c2 = st.columns(2)
            if c1.button("🆕 New Chat"):
                st.session_state.last_result = ""
                st.rerun()
            c2.download_button("📥 Download txt", st.session_state.last_result, "prompt.txt")
        else:
            user_input = st.text_area("Describe the prompt you need...", height=150)
            if st.button("GENERATE"):
                if user_input:
                    with st.spinner("AI is thinking..."):
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        response = model.generate_content(user_input)
                        st.session_state.last_result = response.text
                        st.session_state.usage_count += 1
                        
                        # Save to Database if Logged In
                        if st.session_state.user:
                            try:
                                supabase.table("user_prompts").insert({
                                    "user_id": st.session_state.user.id,
                                    "input_text": user_input,
                                    "output_text": response.text
                                }).execute()
                            except Exception as db_err:
                                st.error(f"Saved to screen, but DB failed: {db_err}")
                        st.rerun()
                else:
                    st.error("Please enter a description!")

elif menu_item == 'History':
    st.title("📜 Your Prompt Library")
    if not st.session_state.user:
        st.info("Log in to save and view your permanent history.")
    else:
        try:
            # Query history for the specific user
            data = supabase.table("user_prompts")\
                .select("*")\
                .eq("user_id", st.session_state.user.id)\
                .order('created_at', descending=True)\
                .execute()
            
            if not data.data:
                st.write("No saved prompts yet. Go to 'New Chat' to create one!")
            else:
                for item in data.data:
                    with st.expander(f"🕒 {item['created_at'][:10]} | {item['input_text'][:40]}..."):
                        st.write(f"**Your Input:**\n{item['input_text']}")
                        st.divider()
                        st.code(item['output_text'])
        except Exception as e:
            st.error("Could not load history. Ensure your 'user_prompts' table is set up in Supabase.")

st.markdown('</div>', unsafe_allow_html=True)
