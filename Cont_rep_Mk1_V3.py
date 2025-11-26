import streamlit as st
from streamlit_lottie import st_lottie
import json
import time 
from google import genai
from google.genai import types

# --- PAGE CONFIG ---
st.set_page_config(page_title="RizenAi Content Repurposer", page_icon="🚀", layout="centered")

# --- CUSTOM CSS (FORCE FIX) ---
st.markdown("""
    <style>
    /* Import Poppins Font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Poppins', sans-serif !important;
    }

    /* THEME COLORS */
    h1, h2, h3 {
        color: white !important;
    }
    
    /* GRADIENT BORDER CONTAINER (The Box) */
    div[data-testid="stForm"] {
        background-color: #00243B;
        border: 2px solid transparent;
        border-image: linear-gradient(to right, #00FFFF, #FF007F) 1;
        border-radius: 10px;
        padding: 30px;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.2);
    }

    /* INPUT FIELDS STYLING */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #001829 !important; 
        color: white !important;
        border: 1px solid #00FFFF !important; 
        border-radius: 5px;
    }
    
    /* --- BUTTON STYLING (NUCLEAR OPTION) --- */
    
    /* Target the button inside the form specifically */
    div[data-testid="stForm"] .stButton > button {
        background: linear-gradient(90deg, #00C6FF 0%, #0072FF 100%) !important;
        color: white !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 700 !important;
        font-size: 18px !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 30px !important;
        
        /* FORCE CENTERING & SIZE */
        width: 60% !important;
        display: block !important;
        margin-left: auto !important;
        margin-right: auto !important;
        
        /* Glow */
        box-shadow: 0 0 15px rgba(0, 198, 255, 0.4);
        transition: all 0.3s ease-in-out;
    }

    /* Hover Effect */
    div[data-testid="stForm"] .stButton > button:hover {
        box-shadow: 0 0 30px rgba(0, 255, 255, 0.9);
        transform: scale(1.02);
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

# Load Animations
LOTTIE_ORDER = "OrderPlaced.json" 
LOTTIE_COOKING = "PrepareFood.json"
LOTTIE_SERVE = "FoodServed.json"

# --- API SETUP ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    api_ready = True
except Exception:
    st.error("⚠️ System Error: GEMINI_API_KEY is missing in Streamlit Secrets.")
    api_ready = False

# --- LOGIC FUNCTIONS (Gemini Free Tier) ---

def api_call_step1_captain(raw_content, user_profile):
    SYSTEM_INSTRUCTION = "You are the 'Captain'. Analyze the user profile and content. Structure a strategic 'Order Block'."
    prompt = f"User Profile: {user_profile}\nContent: {raw_content[:500]}..."
    response = client.models.generate_content(
        model='gemini-2.5-flash', contents=prompt,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION, temperature=0.3)
    )
    return response.text

def api_call_step2_sous_chef(order_block, raw_content):
    SYSTEM_INSTRUCTION = "You are the 'Sous Chef' (GPT-4 Mimic). Create a detailed Production Prompt instructions list."
    prompt = f"Order Block: {order_block}\nOriginal Content: {raw_content}"
    response = client.models.generate_content(
        model='gemini-2.5-flash', contents=prompt,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION, temperature=0.5)
    )
    return response.text

def api_call_step3_chef(production_prompt):
    SYSTEM_INSTRUCTION = "You are the 'Chef' (Claude Mimic). Write human-like, nuanced content deliverables."
    response = client.models.generate_content(
        model='gemini-2.5-flash', contents=production_prompt,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION, temperature=0.8)
    )
    return response.text

# --- MAIN UI LAYOUT ---

# 1. Header Section
st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>RizenAi Content Repurposer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px; margin-top: 0;'>Turn one piece of older content into many</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #00FFFF; font-style: italic;'>“Good stories never die; They are just retold time and over again”</p>", unsafe_allow_html=True)
st.write("") # Spacer

# 2. The Form (Blueprint Input)
with st.form("blueprint_form"):
    st.markdown("### Your Blueprint (The Man-Machine Teaming Input)")
    st.markdown("---")
    
    # Row 1
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**My Name**")
        name = st.text_input("My Name", placeholder="Mandatory: e.g., Sudip", label_visibility="collapsed")
    with col2:
        st.markdown("**My Profession (20 words max)**")
        profession = st.text_input("My Profession", placeholder="Mandatory: e.g., Solopreneur Coach focused on...", label_visibility="collapsed")
    
    # Row 2
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("**Objective for Repurposing (e.g., Reach More People)**")
        objective = st.text_input("Objective", placeholder="Reach More People (Audience Growth)", label_visibility="collapsed")
    with col4:
        st.markdown("**Desired Tone & Style (e.g., Casual and Friendly)**")
        tone = st.text_input("Tone", placeholder="Informative and Professional", label_visibility="collapsed")

    # Row 3 (Full Width)
    st.markdown("**Your Original Content (up to 200 words recommended)**")
    raw_content = st.text_area("Content", placeholder="Mandatory: Paste your original article, transcript, or long-form content here...", height=150, label_visibility="collapsed")

    # Row 4 (Full Width)
    st.markdown("**Any Extra Vital Information (e.g., specific keywords, call to action)**")
    extra_info = st.text_input("Extra Info", placeholder="Optional: e.g., Primary CTA is 'Visit rizenai.co'...", label_visibility="collapsed")

    st.write("") # Spacer
    
    # THE BIG BUTTON (CENTERED & GLOWING)
    submitted = st.form_submit_button("🚀 Plug & Play: Repurpose Content Now")

# --- 3. EXECUTION LOGIC (Animations & API) ---
if submitted:
    if not raw_content or not name or not profession:
        st.error("⚠️ Please fill in all mandatory fields (Name, Profession, Content).")
    elif not api_ready:
        st.error("System API Key missing.")
    else:
        # Combine inputs for the AI
        user_profile = f"Name: {name}, Profession: {profession}, Objective: {objective}, Tone: {tone}, Extra: {extra_info}"
        
        progress_container = st.empty()
        
        # STEP 1: ORDER (Gemini)
        with progress_container.container():
            st.subheader("Step 1: The Chef Takes the Order 📝")
            st_lottie(load_lottiefile(LOTTIE_ORDER), height=200, key="order", loop=True)
            st.info("Gemini is structuring your requirements...")
        order_block = api_call_step1_captain(raw_content, user_profile)
        
        # STEP 2: PREP (ChatGPT Mimic)
        progress_container.empty()
        with progress_container.container():
            st.subheader("Step 2: Tossed in the Wok! 🔥")
            st_lottie(load_lottiefile(LOTTIE_COOKING), height=200, key="prep", loop=True)
            st.warning("Drafting the production blueprint...")
        production_prompt = api_call_step2_sous_chef(order_block, raw_content)
        
        # STEP 3: SERVE (Claude Mimic)
        progress_container.empty()
        with progress_container.container():
            st.subheader("Step 3: Final Plating... 🍽️")
            st_lottie(load_lottiefile(LOTTIE_SERVE), height=200, key="serve", loop=True)
            st.success("Cooking final deliverables...")
        final_output = api_call_step3_chef(production_prompt)
        
        # FINAL DISPLAY
        progress_container.empty()
        st.balloons()
        st.markdown("<h2 style='text-align: center; color: #00FFFF;'>🎉 Content Ready!</h2>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(final_output)
        st.download_button("📥 Download Content", data=final_output, file_name="rizenai_content.md", use_container_width=True)

# --- FOOTER ---
st.markdown("<div class='footer'>© RizenAi.Co | All Rights Reserved</div>", unsafe_allow_html=True)
