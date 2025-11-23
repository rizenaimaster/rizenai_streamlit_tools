import streamlit as st
import google.generativeai as genai
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Content Repurposer", page_icon="🚀")

# Hide Streamlit's default menu to make it look like a pro app
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 2. SETUP GEMINI AI ---
# We try to get the key from the system secrets (the hidden safe)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    api_ready = True
except Exception:
    st.error("⚠️ System Error: API Key is missing. Please configure secrets on Streamlit Cloud.")
    api_ready = False

# --- 3. USER INTERFACE (The Form) ---
st.title("🚀 Content Repurposing System")
st.markdown("Turn one piece of content into multiple platform-ready formats instantly.")

with st.form("repurpose_form"):
    st.subheader("1. Profile & Goals")
    col1, col2 = st.columns(2)
    with col1:
        user_name = st.text_input("Your Name", placeholder="e.g., Aarav")
        profession = st.text_input("Profession", placeholder="e.g., Digital Marketer")
    with col2:
        objective = st.text_input("Objective", placeholder="e.g., Lead Generation")
        tone_style = st.text_input("Tone & Style", placeholder="e.g., Witty, Professional")
    
    target_platforms = st.multiselect(
        "Target Platforms", 
        ["LinkedIn", "Twitter/X Thread", "Instagram Reel Script", "Blog Post", "Email Newsletter", "YouTube Short"],
        default=["LinkedIn", "Twitter/X Thread"]
    )
    
    st.subheader("2. Original Content")
    original_content = st.text_area("Paste your draft/content here:", height=200, placeholder="Paste your article, script, or rough notes here...")
    
    submitted = st.form_submit_button("🚀 Run Repurposing System")

# --- 4. THE INVISIBLE WORKFLOW (Backend) ---
if submitted and api_ready:
    if not original_content:
        st.warning("⚠️ Please paste some content first.")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # --- STEP 1: THE CAPTAIN (Structure) ---
            status_text.text("Step 1/3: Captain Gemini is analyzing trends...")
            
            step1_prompt = f"""
            You are the 'Captain' of the Content Repurposing System.
            Analyze this user profile and create a structured STRATEGY JSON.
            
            USER DATA:
            Name: {user_name} | Profession: {profession}
            Objective: {objective} | Tone: {tone_style}
            Platforms: {', '.join(target_platforms)}
            
            Output JSON ONLY: {{ "strategy_summary": "...", "core_message": "..." }}
            """
            
            response_1 = model.generate_content(step1_prompt)
            strategy_data = response_1.text
            progress_bar.progress(33)
            time.sleep(1) 

            # --- STEP 2: THE SOUS CHEF (Blueprint) ---
            status_text.text("Step 2/3: Drafting the blueprints...")
            
            step2_prompt = f"""
            You are the 'Sous Chef'. Create detailed INSTRUCTIONS for a writer based on this strategy.
            
            STRATEGY: {strategy_data}
            ORIGINAL CONTENT: {original_content}
            
            Output detailed instructions for writing posts for: {', '.join(target_platforms)}.
            """
            
            response_2 = model.generate_content(step2_prompt)
            blueprint = response_2.text
            progress_bar.progress(66)
            time.sleep(1)

            # --- STEP 3: THE CHEF (Final Output) ---
            status_text.text("Step 3/3: Cooking the final content...")
            
            step3_prompt = f"""
            You are the 'Chef'. Write the final content exactly following these instructions.
            
            INSTRUCTIONS:
            {blueprint}
            """
            
            response_3 = model.generate_content(step3_prompt)
            final_output = response_3.text
            
            progress_bar.progress(100)
            status_text.success("✅ Done! Here is your content:")
            
            st.markdown("---")
            st.markdown(final_output)
            
            # Download button
            st.download_button("📥 Download Text", data=final_output, file_name="repurposed.txt")

        except Exception as e:
            st.error(f"An error occurred: {e}")
