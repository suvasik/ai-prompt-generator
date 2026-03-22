# --- 6. PAGE ROUTING (Fixed & Stable) ---

# This ensures that 'tab' is always a string and matches our conditions
current_tab = str(tab)

if current_tab == 'Generator' or current_tab == 'Architect':
    # --- TUTORIAL SECTION (Beginner Friendly) ---
    with st.expander("📖 New here? See how it works"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### 1. Idea 💡")
            st.caption("Type a basic concept like 'Workout plan'.")
        with col2:
            st.markdown("### 2. Build 🏗️")
            st.caption("We turn it into a professional prompt.")
        with col3:
            st.markdown("### 3. Result 🚀")
            st.caption("Copy and use in ChatGPT or Gemini!")

    st.divider()

    # --- GENERATOR LOGIC ---
    if not st.session_state.user and st.session_state.usage_count >= 3:
        st.error("💡 Free limit reached. Please login to continue!")
    else:
        if st.session_state.last_result:
            st.markdown("### ✨ Your Engineered Prompt")
            st.code(st.session_state.last_result, language="markdown")
            
            # Professional JS Copy Utility
            s_text = st.session_state.last_result.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "")
            copy_button_html = f"""
                <button onclick="navigator.clipboard.writeText(`{s_text}`).then(() => alert('Copied!'))" 
                style="width: 100%; height: 45px; background: linear-gradient(45deg, #00f2fe, #4facfe); border: none; border-radius: 12px; color: #050b1a; font-weight: bold; cursor: pointer; width:100%;">
                📋 Copy Result
                </button>
            """
            c1, c2 = st.columns(2)
            with c1: components.html(copy_button_html, height=70)
            with c2:
                if st.button("🆕 Start New"):
                    st.session_state.last_result = ""; st.rerun()
        else:
            st.title("🚀 Prompt Studio")
            prompt_input = st.text_area("What are we creating today?", height=150, placeholder="Enter a basic idea...")
            
            if st.button("GENERATE MASTERPIECE"):
                if prompt_input:
                    with st.spinner("Engineering..."):
                        try:
                            model = genai.GenerativeModel('gemini-2.5-flash')
                            # Choice B: Structured Prompt Logic
                            instruct = "Act as a Master Prompt Engineer. Refine this idea into a professional prompt with Persona, Task, and Constraints: "
                            response = model.generate_content(instruct + prompt_input)
                            
                            st.session_state.last_result = response.text
                            st.session_state.usage_count += 1
                            
                            # Database Save
                            if st.session_state.user:
                                supabase.postgrest.auth(st.session_state.access_token)
                                supabase.table("user_prompts").insert({
                                    "user_id": st.session_state.user.id,
                                    "input_text": prompt_input, 
                                    "output_text": response.text
                                }).execute()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Generation Error: {e}")

elif current_tab == 'My Library' or current_tab == 'Vault':
    st.title("📚 Your Prompt Vault")
    # ... (Keep your Library code here)
