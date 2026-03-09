import streamlit as st
from google import genai
from google.genai import types
from supabase import create_client

# --- 1. BACKEND SETUP ---
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()
client = genai.Client(api_key=st.secrets["GEMINI_KEY"])

# --- 2. THE SYSTEM ARCHITECT INSTRUCTION ---
# This is the "Brain" of your project. 
# It tells the AI exactly how to transform a simple idea into a masterpiece.
ARCHITECT_SYSTEM_PROMPT = """
You are a Professional Prompt Engineer. Your ONLY task is to transform user ideas into high-quality, structured AI prompts.

When the user provides an idea, generate a response following this EXACT structure:
1. **Persona**: Who should the AI act as?
2. **Context**: What background info does the AI need?
3. **Task**: What is the specific goal?
4. **Constraints**: What are the limits (word count, tone, things to avoid)?
5. **Output Format**: How should the result look (Table, Markdown, Code, etc.)?

Output the final result as a clean, copyable block of text. Do NOT be conversational. Do NOT say "Here is your prompt." Just provide the engineered prompt.
"""

# --- 3. UI LAYOUT ---
st.title("🏗️ Professional Prompt Architect")
st.write("Turn your 5-word idea into a 5-star prompt.")

user_idea = st.text_area("What is your idea?", placeholder="e.g., A meal plan for a busy student")

if st.button("Generate Master Prompt"):
    if user_idea:
        with st.spinner("Engineering..."):
            # Using Gemini 2.5 Flash with the System Instruction
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Transform this idea: {user_idea}",
                config=types.GenerateContentConfig(
                    system_instruction=ARCHITECT_SYSTEM_PROMPT,
                    temperature=0.7 # Slight creativity for better expansion
                )
            )
            
            final_prompt = response.text
            
            # --- DISPLAY RESULT ---
            st.subheader("🚀 Your Engineered Prompt")
            st.markdown("Copy the text below and paste it into ChatGPT, Gemini, or Claude.")
            st.code(final_prompt, language="markdown")
            
            # --- LOG TO SUPABASE ---
            if "user" in st.session_state and st.session_state.user:
                supabase.table("user_prompts").insert({
                    "user_id": st.session_state.user.id,
                    "input_text": user_idea,
                    "output_text": final_prompt
                }).execute()
    else:
        st.warning("Please enter an idea first.")
