import streamlit as st
from streamlit_lottie import st_lottie
import json
import time
from google import genai
from google.genai import types

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="RizenAi 7-Day Content System", page_icon="📅", layout="centered")

# --- CUSTOM CSS (Midnight Blue Theme & Styling) ---
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

    /* --- BUTTON STYLING --- */
    .stButton > button {
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

    .stButton > button:hover {
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
if 'day_content' not in st.session_state:
    st.session_state.day_content = []
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
    You are an expert Content Strategist with deep knowledge of digital trends for late 2024 and 2025.
    Your goal is to suggest 3 highly relevant, engaging content series topics based on the user's profile.
    
    For each option, provide:
    1. A Catchy Series Title
    2. A 1-sentence 'Why this works now' justification based on current trends.
    
    Output MUST be a valid JSON array of strings. 
    Example: ["Title 1 - Why it works", "Title 2 - Why it works", "Title 3 - Why it works"]
    """
    
    # Determine input context based on mode
    input_context = user_input_data.get('topic_seed') if mode == "EXPAND" else "No specific topic provided. Find the best opportunity."

    prompt_context = f"""
    User Profile:
    Niche: {user_input_data['niche']}
    Audience: {user_input_data['audience']}
    Goal: {user_input_data['goal']}
    Tone: {user_input_data['tone']}
    
    Mode: {mode} (If EXPAND, build on input. If FIND, suggest new high-potential topics).
    Input: {input_context}
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
        return ["Option 1: Trends Analysis", "Option 2: How-To Guide", "Option 3: Common Mistakes"]

def generate_7_day_plan(selected_topic, user_data):
    """
    Step 4 Logic: The Heavy Lifting.
    1. Strategy (ChatGPT Mimic)
    2. Writing (Claude Mimic)
    Returns the full text content.
    """
    
    platforms_list = ", ".join(user_data['platforms'])

    # PHASE 1: STRATEGY (ChatGPT Persona - Logic & Structure)
    strat_system = """
    You are a Master Content Planner (modeled after GPT-4's reasoning).
    Create a detailed 7-day outline for this topic. 
    Focus on narrative flow, engagement hooks, and high value.
    Do NOT write the posts yet. Just the plan.
    """
    
    strat_prompt = f"""
    Plan a 7-Day Content Series.
    Topic: {selected_topic}
    Audience: {user_data['audience']}
    Platforms: {platforms_list}
    Goal: {user_data['goal']}
    """
    
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
    1. No AI cliches ('Unlock', 'Unleash', 'In today's world', 'Deep dive').
    2. Write in a human, engaging voice matching the user's tone.
    3. For EACH DAY, write specific content for EACH selected platform.
       - Label them clearly (e.g., [LinkedIn], [Twitter]).
       - Include specific CTAs and Hashtags for each.
    4. Add a small 'How-To Guide' at the very start of the file.
    5. Include 'Game Mode' nudges (fun challenges) for each day.
    
    FORMAT:
    The output must be a single text stream.
    Use the exact delimiter '--- DAY [Number] ---' to separate days.
    Example:
    --- DAY 1 ---
    (Content for Day 1)
    --- DAY 2 ---
    (Content for Day 2)
    """
    
    write_prompt = f"""
    Execute this Plan and write the full content.
    User Tone: {user_data['tone']}
    Target Platforms: {platforms_list}
    
    STRATEGY BLUEPRINT:
    {strategy}
    """
    
    final_response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=write_prompt,
        config=types.GenerateContentConfig(system_instruction=write_system, temperature=0.8)
    )
    return final_response.text


# --- UI NAVIGATION & RENDERING ---

# --- SCREEN 1: WELCOME ---
if st.session_state.stage == 'SCREEN_1':
    st.markdown("<h1 style='font-size: 42px;'>RizenAi 7-Day Content System</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1,2])
    with col1:
        st_lottie(load_lottiefile(LOTTIE_WELCOME), height=150, loop=True)
    with col2:
        st.markdown("### Stop the Chaos. Start the Streak.")
        st.write("Turn one idea into a week of high-impact content. Guided, strategic, and done for you.")
    
    st.write("")
    
    # Guide Button (Fake Download for Demo - You can link a real file)
    with st.expander("📖 Read the User Guide"):
         st.info("This tool will ask you a few questions, find the perfect angle, and generate 7 days of posts for LinkedIn, Twitter, and more.")
    
    st.write("")
    if st.button("Start My 7-Day Journey 🚀"):
        st.session_state.stage = 'SCREEN_2'
        st.rerun()

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
        
        # We use columns to simulate two buttons for path selection
        col1, col2 = st.columns(2)
        with col1:
            submitted_a = st.form_submit_button("Path A: I have a Topic")
        with col2:
            submitted_b = st.form_submit_button("Path B: Find Topic for Me")
            
        if submitted_a:
            if not niche or not audience:
                st.error("Please fill in the basics above.")
            else:
                st.session_state.mode = "EXPAND"
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
    
    with st.form("topic_input_form"):
        topic_in = st.text_input("Enter your main topic or idea:", placeholder="e.g., Imposter Syndrome in new business owners")
        submit_topic = st.form_submit_button("Generate Strategy Options")
        
        if submit_topic:
            if not topic_in:
                st.error("Please enter a topic.")
            else:
                st.session_state.user_data = st.session_state.temp_data_cache
                st.session_state.user_data['topic_seed'] = topic_in
                st.session_state.mode = "EXPAND"
                st.session_state.stage = 'SCREEN_3_LOADING'
                st.rerun()

# --- SCREEN 3: LOADING & OPTIONS ---
elif st.session_state.stage == 'SCREEN_3_LOADING':
    st.markdown("### 🧠 Analyzing Market Trends...")
    st_lottie(load_lottiefile(LOTTIE_COOKING), height=200, key="cooking_analysis")
    
    # Generate Options using Gemini
    options = generate_topic_options(st.session_state.user_data, st.session_state.mode)
    st.session_state.topic_options = options
    st.session_state.stage = 'SCREEN_3_SELECTION'
    st.rerun()

elif st.session_state.stage == 'SCREEN_3_SELECTION':
    st.markdown("## 🎯 Select your 7-Day Strategy")
    st.write("Based on current trends (Dec 2025), here are the best angles for you:")
    
    with st.form("selection_form"):
        choice = st.radio("Choose one:", st.session_state.topic_options)
        
        submit_selection = st.form_submit_button("Lock in Strategy & Generate")
        
        if submit_selection:
            st.session_state.selected_topic = choice
            st.session_state.stage = 'SCREEN_4_GENERATING'
            st.rerun()

# --- SCREEN 4: GENERATION ---
elif st.session_state.stage == 'SCREEN_4_GENERATING':
    st.markdown("### 🏗️ Building your 7-Day Content System...")
    st_lottie(load_lottiefile(FoodServed.json), height=200, key="delivering_final")
    st.info("Gemini is creating your strategy... drafting scripts... and polishing hooks...")
    
    # Full Generation
    full_content = generate_7_day_plan(st.session_state.selected_topic, st.session_state.user_data)
    st.session_state.final_content = full_content
    
    # Parse into days (Simple split by delimiter)
    # We split by "--- DAY" to separate the days. 
    # The first part [0] will likely be the "How To Guide" or Intro.
    content_parts = full_content.split("--- DAY")
    
    # Store parts in session state
    st.session_state.intro_content = content_parts[0] if len(content_parts) > 0 else ""
    st.session_state.daily_content = []
    
    # Re-add the "Day X" label to the split parts
    for i, part in enumerate(content_parts[1:]):
        day_num = i + 1
        st.session_state.daily_content.append(f"**Day {day_num}**\n\n" + part)
    
    st.session_state.day_revealed = 1
    st.session_state.stage = 'SCREEN_5_RESULT'
    st.rerun()

# --- SCREEN 5: FINAL DASHBOARD (The Reveal) ---
elif st.session_state.stage == 'SCREEN_5_RESULT':
    st.balloons()
    st.markdown("## 🎉 You are all set to rule the week!")
    st.success("Your 7-Day Series is ready. Click below to reveal each day.")
    
    # 1. Show Intro/Guide First
    with st.expander("📘 READ FIRST: Your How-To Guide", expanded=False):
        st.markdown(st.session_state.intro_content)
    
    # 2. Reveal Mechanism
    # We only show days up to the 'day_revealed' counter
    for i in range(st.session_state.day_revealed):
        if i < len(st.session_state.daily_content):
            day_text = st.session_state.daily_content[i]
            # We use expanders for each day
            with st.expander(f"📅 Content for Day {i+1}", expanded=True):
                st.markdown(day_text)
    
    # 3. The "Next Day" Button
    # Only show if there are more days to reveal
    if st.session_state.day_revealed < len(st.session_state.daily_content):
        if st.button("👇 Generate Next Day"):
            st.session_state.day_revealed += 1
            st.rerun()
    else:
        st.info("✨ All 7 Days Revealed!")

    st.markdown("---")
    
    # 4. Single File Download
    # This downloads the original full text returned by the LLM
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
