import streamlit as st
from streamlit_lottie import st_lottie
import json
import time # Used for simulation, you will replace these sleeps with your API calls

# --- Configuration: Theme & Custom Fonts ---

# CUSTOM CSS FOR FONT & GRADIENT BORDER
st.markdown(
    """
    <style>
    /* 1. Global Font: Poppins */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Poppins', sans-serif !important;
    }

    /* 2. Gradient Border for the Main App Container (1mm thick) */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        
        /* Bright Gradient Border */
        border: 1px solid transparent; 
        border-image: linear-gradient(to right, #FF007F, #00FFFF, #FF7F00) 1;
        border-image-slice: 1;
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.4); /* Subtle Neon Glow */
        border-radius: 5px; /* Optional: adds a slight curve to the border */
    }
    
    /* 3. Button Hover Effect (Making the Aqua pop) */
    .stButton>button:hover {
        border-color: #00FFFF !important;
        color: black !important;
        background-color: #00FFFF !important;
        box-shadow: 0 0 15px #00FFFF;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Lottie Animation Setup ---

# Function to load Lottie URL/JSON from a local file path
@st.cache_data
def load_lottiefile(filepath: str):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Error: Lottie file not found at {filepath}")
        return None

# Lottie File Paths (As provided by the user)
LOTTIE_ORDER = "OrderPlaced.json" 
LOTTIE_COOKING = "PrepareFood.json"
LOTTIE_SERVE = "FoodServed.json"

# --- LLM Placeholder Functions (REPLACE WITH YOUR ACTUAL CODE) ---

# Replace these placeholder functions with your actual LLM integration logic
def api_call_step1(content):
    # This is where your Gemini call (structuring the Order Block) goes
    time.sleep(3) # Simulate 3 seconds of API call
    return f"Structured Order Block from: {content[:30]}..."

def api_call_step2(order_block):
    # This is where your ChatGPT call (drafting the Production Prompt) goes
    time.sleep(4) # Simulate 4 seconds of API call
    return f"Production Prompt from: {order_block[:30]}..."

def api_call_step3(prompt):
    # This is where your Claude call (final deliverables) goes
    time.sleep(5) # Simulate 5 seconds of API call
    # Replace this with your final list of outputs (e.g., twitter_post, blog_outline, etc.)
    return {
        "twitter": "This is the final, polished Twitter Post.",
        "blog": "This is the final Blog Outline.",
        "linkedin": "This is the final LinkedIn Post."
    }

# --- Main Streamlit Application ---

st.title("The RizenAi Content Kitchen")
st.caption("One idea. Endless content. Maximum fun.")

# 1. User Input Section (The "Ingredient")
st.markdown("### 🧈 The Raw Idea (Your Ingredient)")
raw_content = st.text_area(
    "Paste your original content, video transcript, or article here:",
    height=250,
    placeholder="e.g., Paste your 10-minute long video script here...",
    key="raw_content"
)

# Container for the dynamic progress animation
progress_container = st.empty()

# 2. Main Generation Button
if st.button("🚀 Send to the Rizen Kitchen", use_container_width=True) and raw_content:
    
    # ------------------ STEP 1: GEMINI (Order Prep) ------------------
    with progress_container.container():
        st.subheader("Step 1: The Chef Takes the Order 📝")
        st_lottie(load_lottiefile(LOTTIE_ORDER), height=200, key="order", loop=True)
        st.info("Gemini is structuring your requirements into an Order Block...")
    
    order_block = api_call_step1(raw_content)

    # ------------------ STEP 2: CHATGPT (Cooking) ------------------
    progress_container.empty() # Clear previous animation
    with progress_container.container():
        st.subheader("Step 2: Tossed in the Wok! 🔥")
        st_lottie(load_lottiefile(LOTTIE_COOKING), height=200, key="cooking", loop=True)
        st.warning("ChatGPT is drafting the blueprint (Production Prompt)...")

    production_prompt = api_call_step2(order_block)

    # ------------------ STEP 3: CLAUDE (Plating) ------------------
    progress_container.empty() # Clear previous animation
    with progress_container.container():
        st.subheader("Step 3: Final Plating... 🍽️")
        st_lottie(load_lottiefile(LOTTIE_SERVE), height=200, key="serving", loop=True)
        st.success("Claude is generating all final deliverables...")

    final_outputs = api_call_step3(production_prompt)
    
    # ------------------ Final Output Display ------------------
    
    progress_container.empty() # Clear the final animation
    st.balloons() # A celebratory effect
    st.header("🎉 Your Order is Ready! The Chef Has Delivered!")
    
    # Use columns to display the final output cleanly
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🐦 Twitter/X Post")
        st.text_area(label="Twitter Content", value=final_outputs["twitter"], height=150, key="output_twitter")

    with col2:
        st.markdown("#### 🔗 LinkedIn Post")
        st.text_area(label="LinkedIn Content", value=final_outputs["linkedin"], height=150, key="output_linkedin")
    
    st.markdown("#### 📝 Blog/Article Outline")
    st.text_area(label="Blog Content", value=final_outputs["blog"], height=250, key="output_blog")

elif not raw_content and st.session_state.get("raw_content"):
    st.warning("Please paste your content into the box above to begin the process.")
