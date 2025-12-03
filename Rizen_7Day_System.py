import streamlit as st
from streamlit_lottie import st_lottie
import json
import time 
from google import genai
from google.genai import types

# --- PAGE CONFIG ---
st.set_page_config(page_title="RizenAi 7-Day Content System", page_icon="📅", layout="centered")

# --- CUSTOM CSS (Theme, Fonts, Button Fix) ---
st.markdown("""
    <style>
    /* Import Poppins Font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Poppins', sans-serif !important;
    }

    /* THEME COLORS */
    h1, h2, h3, p, li, label {
        color: white !important;
    }
    
    /* GRADIENT BORDER CONTAINER */
    div[data-testid="stForm"] {
        background-color: #00243B;
        border: 2px solid transparent;
        border-image: linear-gradient(to right, #00FFFF, #FF007F) 1;
        border-radius: 10px;
        padding: 30px;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.2);
    }

    /* INPUT FIELDS STYLING */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div > div {
        background-color: #001829 !important; 
        color: white !important;
        border: 1px solid #00FFFF !important; 
        border-radius: 5px;
    }
    
    /* DROPDOWN MENU TEXT COLOR FIX */
    ul[data-testid="stSelectboxVirtualDropdown"] li {
        color: black !important; /* Needs to be black to show on white dropdown */
    }

    /* --- BUTTON STYLING (BRUTE FORCE FIX) --- */
    div[data-testid="stForm"] button {
        background: linear-gradient(90deg, #00C6FF 0%, #0072FF 100%) !important;
        color: white !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 700 !important;
        font-size: 20px !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 15px 0px !important;
        
        /* Full Width & Centered */
        width: 100% !important;
        display: block !important;
        margin: 0 auto !important;
        
        box-shadow: 0 0 15px rgba(0, 198, 255, 0.4);
        transition: all 0.3s ease-in-out;
    }

    div[data-testid="stForm"] button:hover {
        box-shadow: 0 0 30px rgba(0, 255, 255, 0.9);
        transform: scale(1.01);
        color: white !important;
    }

    /* FOOTER STYLING */
    .footer {
        text-align: center;
        color: #888888;
        font-size: 12px;
        margin-top: 50px;
    }
    </style>
""", unsafe_allow_html=True)

# --- ASSET LOADING ---
@st.cache_data
def load_lottiefile(filepath: str):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

# Animations (Ensure these JSONs are in your Repo)
LOTTIE_ANALYSIS = "OrderPlaced.json"  # Reusing Order graphic
LOTTIE_STRATEGY = "PrepareFood.json" # Reusing Cooking graphic
LOTTIE_DELIVERY = "FoodServed.json"   # Reusing Serving graphic

# --- API SETUP ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    api_ready = True
except Exception:
    st.error("⚠️ System Error: GEMINI_API_KEY is missing in Streamlit Secrets.")
    api_ready = False

# --- CORE LOGIC FUNCTIONS (The 3-Step Workflow) ---

def step1_topic_architect(user_profile, topic_input, mode):
    """Step 1: Gemini (Native) - Analyzes market fit & trends."""
    
    SYSTEM_INSTRUCTION = """
    You are the 'Topic Architect' of the RizenAi system.
    Your strength is SITUATIONAL AWARENESS & MARKET TRENDS.
    Your goal: Analyze the user's request and define a high-potential 'Content Angle'.
    
    If Mode is 'Expand Topic': Analyze the user's topic against current trends.
    If Mode is 'Find Topic': Suggest the best high-performing topic for their profession right now.
    
    Output MUST be a structured 'Topic Blueprint' defining:
    1. The Core Theme
    2. The Unique Angle (The 'Why')
    3. The Target Audience Persona
    """
    
    prompt = f"""
    Analyze this request.
    
    USER PROFILE: {user_profile}
    MODE: {mode}
    USER INPUT: {topic_input}
    
    Create a strategic Topic Blueprint.
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash', 
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.3 # Strict logic
        )
    )
    return response.text

def step2_series_strategist(topic_blueprint):
    """Step 2: Mimic ChatGPT - Drafts the 7-Day Plan & Instructions."""
    
    SYSTEM_INSTRUCTION = """
    You are the 'Series Strategist'. You are modeled after GPT-4's comprehensive reasoning.
    Your role: Take the Topic Blueprint and architect a 7-Day Content Series Plan.
    
    STRUCTURE REQUIRED:
    - Day 1 to Day 7 breakdown.
    - For each day: Define the Hook, the Value Format (Story, Listicle, Video, etc.), and the Core Message.
    - Define the "Game Mode" Nudges (optional challenges for the user).
    - Draft specific instructions for the Writer (Step 3) on tone and formatting.
    
    Do NOT write the final posts yet. Create the STRATEGY PLAN only.
    """
    
    prompt = f"""
    Create a comprehensive 7-Day Content Strategy based on this Blueprint:
    
    BLUEPRINT: {topic_blueprint}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash', 
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.5 # Balanced logic/creativity
        )
    )
    return response.text

def step3_content_producer(series_strategy):
    """Step 3: Mimic Claude - Writes the actual posts and guide."""
    
    SYSTEM_INSTRUCTION = """
    You are the 'Creative Director'. You are modeled after Claude 3 Opus.
    Your role: Write the final, polish content deliverables.
    
    CRITICAL WRITING RULES:
    1. Write like a human. Nuanced, engaging, varied sentence structure.
    2. NO AI CLICHES (Avoid: 'Unlock', 'Unleash', 'In today's world', 'Deep dive').
    3. Format the output as a single, clean text stream delimited by '--- DAY X ---'.
    
    DELIVERABLES TO GENERATE:
    1. The 7-Day Content Scripts (Platform-ready).
    2. A brief 'How-To' guide on posting this series.
    3. The 'Game Mode' challenges for the user.
    """

    prompt = f"""
    Execute this Strategy and generate the final content series:
    
    STRATEGY: {series_strategy}
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash', 
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.8 # High creativity
        )
    )
    return response.text

# --- MAIN UI LAYOUT ---

# Header
st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>RizenAi 7-Day Content System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px; margin-top: 0;'>One Topic. Seven Days. Zero Chaos.</p>", unsafe_allow_html=True)
st.write("") 

# Form
with st.form("seven_day_form"):
    st.markdown("### 🛠️ Configure Your Content Engine")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("My Name", placeholder="e.g. Sarah")
        profession = st.text_input("My Profession", placeholder="e.g. Graphic Designer")
    with col2:
        tone = st.text_input("My Voice/Tone", placeholder="e.g. Witty & Authentic")
        # Select Mode
        mode = st.selectbox("What do you want to do?", 
                            ["(A) Expand a Topic I Have", "(B) Find a Topic for Me"])
    
    st.markdown("**Your Input (The Seed)**")
    if mode == "(A) Expand a Topic I Have":
        user_input = st.text_area("Enter your topic/idea:", placeholder="e.g. 'Why branding is more than just a logo'", height=100)
    else:
        user_input = st.text_area("Describe your target audience & goal (so we can find a topic):", placeholder="e.g. 'I want to reach startup founders who need design help'", height=100)

    st.write("") 
    
    submitted = st.form_submit_button("🚀 Launch 7-Day System")

# --- EXECUTION LOGIC ---
if submitted:
    if not name or not profession:
         st.error("⚠️ Please fill in Name and Profession.")
    elif not user_input:
         st.error("⚠️ Please provide the Topic or Audience info.")
    elif not api_ready:
         st.error("System API Key missing.")
    else:
        user_profile = f"Name: {name}, Profession: {profession}, Tone: {tone}"
        
        progress_container = st.empty()
        
        # STEP 1: ARCHITECT (Gemini)
        with progress_container.container():
            st.subheader("Step 1: Analyzing Market Trends... 📊")
            st_lottie(load_lottiefile(LOTTIE_ANALYSIS), height=200, key="1", loop=True)
            st.info("Gemini is finding the perfect angle for your series...")
        
        topic_blueprint = step1_topic_architect(user_profile, user_input, mode)
        time.sleep(1)

        # STEP 2: STRATEGIST (ChatGPT Mimic)
        progress_container.empty()
        with progress_container.container():
            st.subheader("Step 2: Designing the 7-Day Arc... 🗺️")
            st_lottie(load_lottiefile(LOTTIE_STRATEGY), height=200, key="2", loop=True)
            st.warning("Building the strategy, CTA, and engagement hooks...")
        
        series_strategy = step2_series_strategist(topic_blueprint)
        time.sleep(1)

        # STEP 3: PRODUCER (Claude Mimic)
        progress_container.empty()
        with progress_container.container():
            st.subheader("Step 3: Writing Final Scripts... ✍️")
            st_lottie(load_lottiefile(LOTTIE_DELIVERY), height=200, key="3", loop=True)
            st.success("Crafting human-like posts and the user guide...")
        
        final_output = step3_content_producer(series_strategy)
        
        # FINAL DISPLAY
        progress_container.empty()
        st.balloons()
        st.markdown("<h2 style='text-align: center; color: #00FFFF;'>🎉 Your 7-Day Series is Ready!</h2>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown(final_output)
        
        # Download Button
        st.download_button(
            label="📥 Download Complete Series (Text File)",
            data=final_output,
            file_name="RizenAi_7Day_Series.txt",
            mime="text/plain",
            use_container_width=True
        )

# --- FOOTER ---
st.markdown("<div class='footer'>© RizenAi.Co | All Rights Reserved</div>", unsafe_allow_html=True)
