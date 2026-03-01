import streamlit as st
import google.generativeai as genai
import streamlit_antd_components as sac
from supabase import create_client, Client

# --- 1. CONFIG & DB SETUP ---
st.set_page_config(page_title="Prompt Studio Pro", page_icon="🪄", layout="wide")

def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()
genai.configure(api_key=st.secrets["GEMINI_KEY"])

# --- 2. ENHANCED INTERACTIVE UI ---
st.markdown("""
    <style>
    /* Gradient Background */
    .stApp { 
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%); 
        background-attachment: fixed; 
    }
    
    /* Interactive Glassmorphism Box */
    .main-box { 
        background: rgba(255, 255, 255, 0.07); 
        backdrop-filter: blur(25px); 
        border-radius: 25px; 
        padding: 40px; 
        border: 1px solid rgba(255, 255, 255, 0.1); 
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
        transition: transform 0.3s ease;
    }
    
    /* Glowing Buttons */
    div.stButton > button { 
        background: linear-gradient(45deg, #00f2fe, #4facfe) !important;
        color: #050b1a !important; 
        font-weight: 800 !important; 
        border-radius: 15px !important; 
        width: 100%; 
        border: none !important;
        height: 50px;
        transition: 0.4s all ease !important;
    }
    div.stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 20px rgba(0, 242, 254, 0.4) !important;
    }

    h1, h2, h3, p, span, label { color: white !important; font-family: 'Inter', sans-serif; }
    
    /* Styled Text Area */
    .stTextArea textarea { 
        background-color: rgba(0,0,0,0.2) !important; 
        color: #00f2fe !important; 
        border: 1px solid rgba(0, 242, 254, 0.2) !important;
        border-radius: 15px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "user" not in st.session_state: st.session_state.user = None
if "access_token" not in st.session_state: st.session_state.access_token = None
if "usage_count" not in st.session_state: st.session_state.usage_count = 0
if "last_result" not in st.session_state: st.session_state.last_result = ""

# --- 4. SIDEBAR AUTH ---
with st.sidebar:
    st.title("👤 Account")
    if st.session_state.user:
        st.markdown(f"✅ **Logged in as:**\n{st.session_state.user.email}")
        if st.button("🚪 Logout"):
            st.session_state.user = None
            st.session_state.access_token = None
            st.rerun()
    else:
        # Simple progress bar for guests
        st.write(f"Guest Usage: {st.session_state.usage_count}/3")
        st.progress(st.session_state.usage_count / 3)
        
        mode = st.radio("Access Mode", ["Login", "Sign Up"], horizontal=True)
        email = st.text_input("Email").strip()
        pw = st.text_input("Password", type="password").strip()
        
        if mode == "Login" and st.button("🚀 Access Account"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": pw})
                st.session_state.user = res.user
                st.session_state.access_token = res.session.access_token
                st.rerun()
            except: st.error("Invalid Credentials.")
        
        if mode == "Sign Up" and st.button("✨ Create Profile"):
            try:
                supabase.auth.sign_up({"email": email, "password": pw})
                st.success("Success! Switch to Login mode.")
            except Exception as e: st.error(f"Error: {e}")

# --- 5. NAVIGATION ---
tab = sac.tabs([
    sac.TabsItem(label='Generator', icon='magic'),
    sac.TabsItem(label='My Library', icon='folder2-open'),
], align='center', variant='toggle', color='cyan')

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# --- 6. PAGE ROUTING ---
if tab == 'Generator':
    if not st.session_state.user and st.session_state.usage_count >= 3:
        st.error("💡 You've reached the free limit. Please Login to continue saving your prompts!")
    else:
        if st.session_state.last_result:
            st.markdown("### ✨ AI Magic Result")
            st.code(st.session_state.last_result, language="markdown")
            
            # COPY & ACTION BUTTONS
            col1, col2, col3 = st.columns([1,1,1])
            with col1:
                if st.button("📋 Copy to Clipboard"):
                    st.copy_to_clipboard(st.session_state.last_result)
                    st.toast("Copied to clipboard!", icon="✅")
            with col2:
                if st.button("🆕 New Chat"):
                    st.session_state.last_result = ""; st.rerun()
            with col3:
                st.download_button("📥 Download", st.session_state.last_result, "ai_prompt.txt")
        else:
            st.title("🚀 Prompt Studio")
            prompt_input = st.text_area("Describe what you want to create...", height=180, placeholder="E.g. Write a viral LinkedIn post about AI trends in 2026...")
            
            if st.button("✨ GENERATE"):
                if prompt_input:
                    with st.spinner("🔮 Consultng the AI..."):
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        response = model.generate_content(prompt_input)
                        st.session_state.last_result = response.text
                        st.session_state.usage_count += 1
                        
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
                else:
                    st.warning("Please enter your idea first!")

elif tab == 'My Library':
    st.title("📚 Saved Library")
    if not st.session_state.user:
        st.info("Log in to view your permanent collection.")
    else:
        try:
            supabase.postgrest.auth(st.session_state.access_token)
            data = supabase.table("user_prompts").select("*").order('created_at', desc=True).execute()
            
            if not data.data:
                st.write("Your library is empty. Start generating!")
            else:
                for item in data.data:
                    with st.expander(f"📦 {item['input_text'][:50]}..."):
                        st.write(f"**Original Request:** {item['input_text']}")
                        st.code(item['output_text'])
                        if st.button(f"Copy This Result", key=item['id']):
                            st.copy_to_clipboard(item['output_text'])
                            st.toast("Prompt copied!")
        except Exception as e:
            st.error(f"Connection Error: {e}")

st.markdown('</div>', unsafe_allow_html=True)
