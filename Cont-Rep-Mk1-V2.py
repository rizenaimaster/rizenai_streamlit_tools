import streamlit as st
import json
import os
import time
from google import genai
from google.genai import types
from google.genai.errors import APIError

# --- Configuration ---
GEMINI_MODEL = 'gemini-2.5-flash-preview-09-2025'

# Initialize API Client secureley
try:
    # Try getting key from Streamlit secrets first, then os environment
    if "GEMINI_API_KEY" in st.secrets:
        API_KEY = st.secrets["GEMINI_API_KEY"]
    else:
        API_KEY = os.getenv("GEMINI_API_KEY")

    if not API_KEY:
        st.warning("GEMINI_API_KEY not found.")
        st.info("Please set the GEMINI_API_KEY in your Streamlit secrets.")
        client = None
    else:
        client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error(f"Error initializing Gemini client: {e}")
    client = None

# --- Custom CSS for RizenAi Styling ---
st.markdown(
    """
    <style>
    /* 1. Import Poppins Font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    /* 2. Global Font and Background */
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    .stApp {
        background-color: #00243B; /* Dark midnight blue */
    }

    /* 3. Gradient Border around the Main Block */
    /* We target the main block container to give it the frame */
    .block-container {
        border: 2px solid transparent;
        background-clip: padding-box, border-box;
        background-origin: padding-box, border-box;
        background-image: linear-gradient(#00243B, #00243B), 
                          linear-gradient(to right, #00FFFF, #FF00FF, #FFD700, #00FFFF); /* Neon Gradient */
        border-radius: 15px;
        padding: 3rem 2rem !important; /* Internal spacing */
        margin-top: 2rem;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.1);
    }

    /* 4. Input Fields Styling */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid #00FFFF !important;
        color: white !important;
        border-radius: 8px;
    }
    /* Focus state for inputs */
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #00BFFF !important;
        box-shadow: 0 0 10px rgba(0, 191, 255, 0.5);
    }
    /* Labels */
    .stMarkdown label, .stTextInput label, .stTextArea label, .stSelectbox label {
        color: #00FFFF !important;
    }

    /* 5. Custom Button Styling (Larger, Aqua Gradient, Glow) */
    .stButton > button {
        width: 100%;
        background: linear-gradient(145deg, #00BFFF, #00FFFF); /* Neon Aqua Gradient */
        color: #00243B !important;
        font-weight: 700 !important;
        font-size: 1.4rem !important; /* Bigger Font */
        padding: 1.25rem !important;      /* Broader/Taller Button */
        border: none;
        border-radius: 0.5rem;
        transition: all 0.3s ease;
        margin-top: 1.5rem; /* Added spacing */
    }
    
    .stButton > button:hover {
        box-shadow: 0 0 20px #00FFFF; /* Slight Glow on Hover */
        transform: scale(1.01);
        color: #00243B !important;
        border: 1px solid rgba(255, 255, 255, 0.5);
    }

    /* 6. Output Card Styling */
    .output-card {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid #00BFFF;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Logic Functions ---

def create_system_instruction(data):
    platforms_str = ', '.join(data['platforms'])
    return f"""
        You are the RizenAi Content Repurposing System Orchestrator. 
        User Profile: Name: {data['name']}, Profession: {data['profession']}, Objective: {data['objective']}, Tone: {data['tone']}
        Target Platforms: {platforms_str}
        Extra Context: {data['extra_info']}
        
        PHASE 1 (Gemini): Analyze trends for {data['profession']}. Define Thematic Focus.
        PHASE 2 (ChatGPT Persona): Draft production prompt based on focus.
        PHASE 3 (Claude Persona): Write final human-like content. Avoid mechanical phrasing.
        
        Original Content:
        {data['original_content']}
        
        OUTPUT FORMAT: Single valid JSON object. Keys = platform names (underscores). Values = content.
        {{
            "{data['platforms'][0].replace(' ', '_')}": "Content..."
        }}
    """

def get_generation_config(platforms):
    properties = {}
    for platform in platforms:
        properties[platform.replace(' ', '_')] = {"type": "string"}
    return types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema={"type": "object", "properties": properties},
        tools=[{"google_search": {}}]
    )

def repurpose_content(data):
    if not client:
        return None
    
    system_instruction = create_system_instruction(data)
    generation_config = get_generation_config(data['platforms'])
    user_query = f"Repurpose this content: {data['original_content']}"
    
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_query,
            config=generation_config,
            system_instruction=system_instruction
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Generation Error: {e}")
        return None

# --- UI Layout ---

# Centered Headers
st.markdown('<h1 style="text-align: center; color: white; margin-bottom: 0px;">RizenAi Content Repurposer</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #d1d5db; margin-top: 5px;">Turn one piece of older content into many</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.1rem; font-style: italic; color: #00FFFF; margin-bottom: 30px;">“Good stories never die; They are just retold time and over again”</p>', unsafe_allow_html=True)

st.markdown('<h3 style="color: #00BFFF; border-bottom: 1px solid #00FFFF; padding-bottom: 5px;">Your Blueprint (The Man-Machine Teaming Input)</h3>', unsafe_allow_html=True)

with st.form("repurpose_form"):
    col1, col2 = st.columns(2)
    with col1:
        user_name = st.text_input("My Name", placeholder="e.g., Sudip")
    with col2:
        profession = st.text_input("My Profession", placeholder="e.g., Solopreneur Coach")

    col3, col4 = st.columns(2)
    with col3:
        objective = st.selectbox("Objective", ["Reach More People", "Boost Engagement", "Promote Service", "Build Authority"])
    with col4:
        tone = st.selectbox("Tone & Style", ["Informative", "Casual/Friendly", "Bold", "Motivational"])
        
    platforms = st.multiselect("Target Platforms", ["LinkedIn Post", "Twitter/X Thread", "Instagram Carousel Script", "Blog Intro", "Email Snippet"], default=["LinkedIn Post"])

    original_content = st.text_area("Original Content (up to 200 words)", height=150)
    extra_info = st.text_input("Extra Info (CTA, Keywords)")

    # Button text change applied here
    submitted = st.form_submit_button("Plug & Play : Repurpose your content now")

if submitted:
    if not user_name or not original_content:
        st.error("Please fill required fields.")
    else:
        form_data = {
            "name": user_name, "profession": profession, "objective": objective,
            "tone": tone, "platforms": platforms, "original_content": original_content,
            "extra_info": extra_info
        }
        
        with st.spinner("Processing..."):
            results = repurpose_content(form_data)
            
            if results:
                st.markdown('<h3 style="color: #00BFFF; margin-top: 30px; text-align: center;">Meal Served! Your Deliverables</h3>', unsafe_allow_html=True)
                for key, content in results.items():
                    platform_name = key.replace('_', ' ')
                    st.markdown(f"""
                    <div class="output-card">
                        <h4 style="color: #00FFFF; margin-bottom: 10px;">{platform_name}</h4>
                        <div style="white-space: pre-wrap; color: #e5e7eb;">{content}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.download_button("Download JSON", data=json.dumps(results, indent=2), file_name="rizenai_content.json", mime="application/json")

st.markdown('<p style="text-align: center; color: #6b7280; font-size: 0.8rem; margin-top: 3rem;">© RizenAi.Co | All Rights Reserved</p>', unsafe_allow_html=True)
