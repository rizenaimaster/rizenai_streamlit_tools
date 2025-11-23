import streamlit as st
from google import genai
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Content Repurposer", page_icon="🚀")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 2. SETUP GEMINI AI (NEW LIBRARY) ---
try:
    # We grab the key you saved in Streamlit Secrets
    api_key = st.secrets["GEMINI_API_KEY"]
    
    # Initialize the NEW Client
    client = genai.Client(api_key=api_key)
    api_ready = True
except Exception:
    st.error("⚠️ System Error: API Key is missing. Please configure secrets on Streamlit Cloud.")
    api_ready = False

# --- 3. USER INTERFACE ---
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

# --- 4. THE INVISIBLE WORKFLOW (NEW MODEL) ---
if submitted and api_ready:
    if not original_content:
        st.warning("⚠️ Please paste some content first.")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # We use the new stable model: gemini-2.5-flash
        # If this fails later, try 'gemini-2.0-flash'
        MODEL_NAME = "gemini-2.5-flash"

        try:
            # --- STEP 1: THE CAPTAIN ---
            status_text.text(f"Step 1/3: Captain Gemini ({MODEL_NAME}) is analyzing trends...")
            
            step1_prompt = f"""
            You are the 'Captain' of the Content Repurposing System.
            Analyze this user profile and create a structured STRATEGY summary.
            
            USER DATA:
            Name: {user_name} | Profession: {profession}
            Objective: {objective} | Tone: {tone_style}
            Platforms: {', '.join(target_platforms)}
            
            Output a concise strategy summary.
            """
            
            # New Library Syntax
            response_1 = client.models.generate_content(
                model=MODEL_NAME, 
                contents=step1_prompt
            )
            strategy_data = response_1.text
            progress_bar.progress(33)
            time.sleep(1) 

            # --- STEP 2: THE SOUS CHEF ---
            status_text.text("Step 2/3: Drafting the blueprints...")
            
            step2_prompt = f"""
            You are the 'Sous Chef'. Create detailed INSTRUCTIONS for a writer based on this strategy.
            
            STRATEGY: {strategy_data}
            ORIGINAL CONTENT: {original_content}
            
            Output detailed instructions for writing posts for: {', '.join(target_platforms)}.
            """
            
            response_2 = client.models.generate_content(
                model=MODEL_NAME, 
                contents=step2_prompt
            )
            blueprint = response_2.text
            progress_bar.progress(66)
            time.sleep(1)

            # --- STEP 3: THE CHEF ---
            status_text.text("Step 3/3: Cooking the final content...")
            
            step3_prompt = f"""
            You are the 'Chef'. Write the final content exactly following these instructions.
            
            INSTRUCTIONS:
            {blueprint}
            """
            
            response_3 = client.models.generate_content(
                model=MODEL_NAME, 
                contents=step3_prompt
            )
            final_output = response_3.text
            
            progress_bar.progress(100)
            status_text.success("✅ Done! Here is your content:")
            
            st.markdown("---")
            st.markdown(final_output)
            
            st.download_button("📥 Download Text", data=final_output, file_name="repurposed.txt")

        except Exception as e:
            st.error(f"An error occurred: {e}")
