import streamlit as st
from streamlit_lottie import st_lottie
import json
import time
from google import genai
from google.genai import types

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="RizenAi 7-Day Content System", page_icon="📅", layout="centered")

# --- CUSTOM CSS (Midnight Blue Theme) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Poppins', sans-serif !important;
        color: #FFFFFF;
    }
    
    /* Backgrounds */
    .stApp {
        background-color: #00243B;
    }
    
    /* Containers */
    div[data-testid="stForm"] {
        background-color: #001829;
        border: 1px solid #00FFFF;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.1);
    }
    
    /* Inputs */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div > div {
        background-color: #00243B !important;
        color: white !important;
        border: 1px solid #005f73 !important;
        border-radius: 8px;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #00C6FF 0%, #0072FF 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        box-shadow: 0 0 20px rgba(0, 198, 255, 0.6);
        transform: scale(1.02);
    }

    /* Radio Buttons */
    .stRadio label {
        color: white !important;
        font-size: 16px !important;
        background-color: #001829;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 5px;
        border: 1px solid #005f73;
        width: 100%;
        display: block;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: white !important;
        text-align: center;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #001829 !important;
        color: white !important;
        border-radius: 8px;
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

# Ensure these exist in your repo
LOTTIE_WELCOME = "OrderPlaced.json" 
LOTTIE_COOKING = "PrepareFood.json"
LOTTIE_DONE = "FoodServed.json"

# --- SESSION STATE INITIALIZATION ---
if 'stage' not in st.session_state:
    st.session_state.stage = 'SCREEN_1'
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'topic_options' not in st.session_state:
    st.session_state.topic_options = []
if 'selected_topic' not in st.session_state:
    st.session_state.selected_topic = ""
if 'final_content' not in st.session_state:
    st.session_state.final_content = ""
if 'day_revealed' not in st.session_state:
    st.session_state.day_revealed = 0

# --- API SETUP ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    api_ready = True
except Exception:
    st.error("⚠️ System Error: GEMINI_API_KEY is missing in Streamlit Secrets.")
    api_ready = False


# --- LOGIC FUNCTIONS ---

def generate_topic_options(user_input_data, mode):
    """
    Step 3A/3C Logic: Generates 3 strategic topic options.
    Gemini acts as a Market Analyst (Situational Awareness).
    """
    system_instruction = """
    You are an expert Content Strategist with deep knowledge of 2024-2025 digital trends.
    Your goal is to suggest 3 highly relevant, engaging content series topics based on the user's profile.
    For each option, provide a Title and a 1-sentence 'Why this works now' justification.
    Return ONLY a JSON array of strings, e.g., ["Topic 1 - Why", "Topic 2 - Why", "Topic 3 - Why"].
    """
    
    prompt_context = f"""
    User Profile: {user_input_data['niche']} | {user_input_data['audience']}
    Goal: {user_input_data['goal']}
    Tone: {user_input_data['tone']}
    Mode: {mode}
    Input: {user_input_data.get('topic_seed', 'Find best topics')}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_context,
            config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.7)
        )
        # Clean markdown if present
        text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text)
    except Exception as e:
        st.error(f"Error generating topics: {e}")
        return ["Option 1: General Industry Trends", "Option 2: How-To Series", "Option 3: Common Mistakes"]

def generate_7_day_plan(selected_topic, user_data):
    """
    Step 4 Logic: The Heavy Lifting.
    1. Strategy (ChatGPT Mimic)
    2. Writing (Claude Mimic)
    Returns the full text content.
    """
    
    # PHASE 1: STRATEGY (ChatGPT Persona - Logic & Structure)
    strat_system = "You are a Master Content Planner (modeled after GPT-4). Create a detailed 7-day outline for this topic. Focus on flow, hooks, and value."
    strat_prompt = f"Plan a 7-Day Series on: {selected_topic}\nContext: {user_data}"
    
    strat_response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=strat_prompt,
        config=types.GenerateContentConfig(system_instruction=strat_system, temperature=0.4)
    )
    strategy = strat_response.text
    
    # PHASE 2: WRITING (Claude Persona - Human & Nuanced)
    write_system = """
    You are a world-class Creative Writer (modeled after Claude 3 Opus).
    Write the full content for the 7-Day Series based on the strategy provided.
    
    RULES:
    1. No AI cliches ('Unlock', 'Unleash', 'In today's world').
    2. Write in a human, engaging voice matching the user's tone.
    3. Include specific CTAs and Hashtags for each day.
    4. Add a small 'How-To Guide' at the start.
    5. Include 'Game Mode' nudges (fun challenges) for each day.
    
    FORMAT:
    Use '--- DAY 1 ---', '--- DAY 2 ---' as delimiters.
    """
    
    write_prompt = f"Execute this plan and write the full content:\n\n{strategy}"
    
    final_response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=write_prompt,
        config=types.GenerateContentConfig(system_instruction=write_system, temperature=0.8)
    )
    return final_response.text


# --- UI NAVIGATION ---

def go_to_screen_2():
    st.session_state.stage = 'SCREEN_2'

def go_to_screen_3(mode):
    # Save Screen 2 Data
    st.session_state.user_data = {
        'niche': niche,
        'audience': audience,
        'goal': goal,
        'tone': tone,
        'platforms': platforms
    }
    st.session_state.mode = mode
    st.session_state.stage = 'SCREEN_3'

def process_topic_selection():
    # Trigger Generation
    if not st.session_state.selected_topic:
        st.warning("Please select a topic.")
        return
    
    st.session_state.stage = 'PROCESSING'
    st.rerun()

def reveal_next_day():
    if st.session_state.day_revealed < 7:
        st.session_state.day_revealed += 1

# --- SCREEN 1: WELCOME ---
if st.session_state.stage == 'SCREEN_1':
    st.markdown("<h1 style='font-size: 42px;'>RizenAi 7-Day System</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1,2])
    with col1:
        st_lottie(load_lottiefile(LOTTIE_WELCOME), height=150, loop=True)
    with col2:
        st.markdown("### Stop the Chaos. Start the Streak.")
        st.write("Turn one idea into a week of high-impact content. Guided, strategic, and done for you.")
    
    st.write("")
    if st.button("Start My 7-Day Journey 🚀"):
        go_to_screen_2()
        st.rerun()
        
    with st.expander("📖 Read the User Guide"):
        st.info("This tool will ask you a few questions, find the perfect angle, and generate 7 days of posts for LinkedIn, Twitter, and more.")
        # Link to download guide from repo (Placeholder)
        st.markdown("[Download Full Guide (PDF)](https://github.com/your-repo/guide.pdf)")

# --- SCREEN 2: DATA COLLECTION ---
elif st.session_state.stage == 'SCREEN_2':
    st.markdown("## 📝 Tell us about your world")
    
    with st.form("data_form"):
        niche = st.text_input("1. My Niche / Industry", placeholder="e.g., Digital Marketing for Solopreneurs")
        audience = st.text_input("2. Who do I want to reach?", placeholder="e.g., Women restarting careers")
        goal = st.text_input("3. What should this content do?", placeholder="e.g., Build authority & trust")
        tone = st.text_input("4. Tone & Style", placeholder="e.g., Empathetic, encouraging, professional")
        platforms = st.multiselect("5. Target Platforms", ["LinkedIn", "Instagram", "Twitter/X", "Facebook", "Blog"], default=["LinkedIn"])
        
        st.markdown("---")
        st.markdown("### Choose your path:")
        col1, col2 = st.columns(2)
        with col1:
            submitted_a = st.form_submit_button("Path A: I have a Topic")
        with col2:
            submitted_b = st.form_submit_button("Path B: Find Topic for Me")
            
        if submitted_a:
            if not niche or not audience:
                st.error("Please fill in the basics above.")
            else:
                st.session_state.topic_mode = "EXPAND"
                # We need one more input for Path A
                st.session_state.temp_data_cache = {'niche': niche, 'audience': audience, 'goal': goal, 'tone': tone, 'platforms': platforms}
                st.session_state.stage = 'SCREEN_2_A_INPUT'
                st.rerun()
                
        if submitted_b:
            if not niche or not audience:
                st.error("Please fill in the basics above.")
            else:
                st.session_state.user_data = {'niche': niche, 'audience': audience, 'goal': goal, 'tone': tone, 'platforms': platforms}
                st.session_state.mode = "FIND"
                st.session_state.stage = 'SCREEN_3_LOADING'
                st.rerun()

# --- SCREEN 2A: TOPIC INPUT (Only for Path A) ---
elif st.session_state.stage == 'SCREEN_2_A_INPUT':
    st.markdown("## 💡 What is your topic?")
    topic_in = st.text_input("Enter your main topic or idea:", placeholder="e.g., Imposter Syndrome in new business owners")
    if st.button("Generate Strategy Options"):
        st.session_state.user_data = st.session_state.temp_data_cache
        st.session_state.user_data['topic_seed'] = topic_in
        st.session_state.mode = "EXPAND"
        st.session_state.stage = 'SCREEN_3_LOADING'
        st.rerun()

# --- SCREEN 3: LOADING & OPTIONS ---
elif st.session_state.stage == 'SCREEN_3_LOADING':
    st.markdown("### 🧠 Analyzing Market Trends...")
    st_lottie(load_lottiefile(LOTTIE_COOKING), height=200, key="cooking")
    
    # Generate Options
    options = generate_topic_options(st.session_state.user_data, st.session_state.mode)
    st.session_state.topic_options = options
    st.session_state.stage = 'SCREEN_3_SELECTION'
    st.rerun()

elif st.session_state.stage == 'SCREEN_3_SELECTION':
    st.markdown("## 🎯 Select your 7-Day Strategy")
    st.write("Based on current trends (Dec 2025), here are the best angles for you:")
    
    choice = st.radio("Choose one:", st.session_state.topic_options)
    
    if st.button("Lock in Strategy & Generate"):
        st.session_state.selected_topic = choice
        st.session_state.stage = 'SCREEN_4_GENERATING'
        st.rerun()

# --- SCREEN 4: GENERATION & REVEAL ---
elif st.session_state.stage == 'SCREEN_4_GENERATING':
    st.markdown("### 🏗️ Building your 7-Day Content System...")
    st_lottie(load_lottiefile(FoodServed.json), height=200, key="delivering")
    
    # Full Generation
    full_content = generate_7_day_plan(st.session_state.selected_topic, st.session_state.user_data)
    st.session_state.final_content = full_content
    
    # Parse into days (Simple split by delimiter)
    # Note: This relies on the AI following the instruction "--- DAY X ---"
    # We will store it as a list for the reveal mechanic
    days = full_content.split("--- DAY")
    # Clean up the split
    st.session_state.day_content = ["Day " + d for d in days if len(d) > 20] 
    
    st.session_state.day_revealed = 1
    st.session_state.stage = 'SCREEN_5_RESULT'
    st.rerun()

# --- SCREEN 5: FINAL DASHBOARD ---
elif st.session_state.stage == 'SCREEN_5_RESULT':
    st.balloons()
    st.markdown("## 🎉 You are all set to rule the week!")
    st.success("Your 7-Day Series is ready. Click below to reveal each day.")
    
    # Reveal Mechanism
    for i in range(st.session_state.day_revealed):
        if i < len(st.session_state.day_content):
            day_text = st.session_state.day_content[i]
            # Extract title if possible, or just use generic Day X
            with st.expander(f"📅 Content for Day {i+1}", expanded=True):
                st.markdown(day_text)
    
    # The "Next Day" Button logic
    if st.session_state.day_revealed < len(st.session_state.day_content):
        if st.button("👇 Generate Next Day"):
            st.session_state.day_revealed += 1
            st.rerun()
    else:
        st.info("✨ All 7 Days Revealed!")

    st.markdown("---")
    
    # Single File Download
    st.download_button(
        label="📥 Download Complete 7-Day Plan (Text File)",
        data=st.session_state.final_content,
        file_name="RizenAi_7Day_Plan.txt",
        mime="text/plain",
        use_container_width=True
    )
    
    # Footer links
    st.markdown("---")
    st.caption("RizenAi - Plug -> Play -> Profit")
    st.markdown("[Instagram](https://instagram.com) | [LinkedIn](https://linkedin.com)")
