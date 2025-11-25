import streamlit as st
import json
import os
import time
from google import genai
from google.genai import types
from google.genai.errors import APIError

# --- Configuration ---
GEMINI_MODEL = 'gemini-2.5-flash-preview-09-2025'
# The API key is loaded from the environment variable GEMINI_API_KEY
# This is the secure method for Streamlit Cloud deployment.
# Streamlit will automatically use st.secrets['GEMINI_API_KEY'] if defined.
# If running locally, ensure GEMINI_API_KEY is set in your system environment.
try:
    API_KEY = os.getenv("GEMINI_API_KEY")
    if not API_KEY:
        st.warning("GEMINI_API_KEY environment variable not found.")
        st.info("Please set the GEMINI_API_KEY in your Streamlit secrets or environment for deployment.")
        client = None
    else:
        client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error(f"Error initializing Gemini client: {e}")
    client = None


# --- Prompt and Instruction Generation ---

def create_system_instruction(data):
    """Generates the multi-phase system instruction for the Gemini model."""
    platforms_str = ', '.join(data['platforms'])
    
    return f"""
        You are the RizenAi Content Repurposing System Orchestrator. Your goal is to execute a high-quality, 
        human-centric 3-phase workflow in one step to ensure the final output is creative, non-mechanical, and ready for publication.

        **User Profile & Goals:**
        - **Name:** {data['name']}
        - **Profession:** {data['profession']}
        - **Objective:** {data['objective']}
        - **Tone/Style:** {data['tone']}
        - **Target Platforms:** {platforms_str}
        - **Extra Context:** {data['extra_info'] or 'None provided.'}

        **Execution Phases (Simulating Multi-LLM Quality):**
        
        1. **PHASE 1 (Captain's Order Block - Gemini Role):** Use Google Search grounding to analyze current digital content trends for {data['profession']} and the target platforms. Define the core **Thematic Focus** and the **Emotional Hook** required for maximum impact in a {data['tone']} style.
        
        2. **PHASE 2 (Sous Chef's Blueprint - ChatGPT Role):** Based on the Captain's Focus, adopt the persona of a senior digital strategist with wide context. Draft a precise, optimized production prompt for each target platform, ensuring structure (hooks, CTAs, thread format, visual cues) is tailored to platform best practices (e.g., LinkedIn for authority, Instagram for visual story). This phase is purely contextual preparation.
        
        3. **PHASE 3 (Chef-de-Partie Production - Claude Role):** Adopt the persona of a human, expert copywriter known for highly creative, authentic, and emotionally resonant content. Write the final repurposed content for each platform. **CRITICAL:** The output MUST avoid repetition, generic AI language, and overly mechanical phrasing. It must sound like an expert human in the {data['tone']} style wrote it. The core message from the Original Content must be preserved, not summarized.

        **Original Content to Repurpose:**
        ---
        {data['original_content']}
        ---

        **Output Format (CRITICAL):**
        You MUST respond only with a single JSON object. The keys must be the platform names (using underscores instead of spaces, e.g., LinkedIn_Post), and the values must be the fully repurposed, human-like content for that platform.

        {{
            "{data['platforms'][0].replace(' ', '_')}": "The human-like repurposed content for Platform 1...",
            // ... continue for all selected platforms
        }}
        
        Do not include any greeting, commentary, or markdown outside of the JSON structure.
        Ensure the JSON is perfectly valid and ready for parsing.
    """

def get_generation_config(platforms):
    """Creates the JSON schema for structured output."""
    properties = {}
    for platform in platforms:
        # Use underscores for JSON keys as per instruction
        properties[platform.replace(' ', '_')] = {"type": "string"}

    return types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema={"type": "object", "properties": properties},
        # Enable Google Search grounding for Phase 1 analysis
        tools=[{"google_search": {}}]
    )


# --- Core Repurposing Function with Retry Logic ---

def repurpose_content(data):
    """Calls the Gemini API to generate repurposed content."""
    if not client:
        return {"Error": "Gemini Client not initialized. Check API Key configuration."}

    system_instruction = create_system_instruction(data)
    generation_config = get_generation_config(data['platforms'])
    
    user_query = f"Original Content to be Repurposed: {data['original_content']}"

    max_retries = 3
    delay = 2  # initial delay in seconds
    
    for attempt in range(max_retries):
        try:
            # 1. Prepare contents
            contents = [
                types.Content(
                    role="user", 
                    parts=[types.Part.from_text(user_query)]
                )
            ]
            
            # 2. Make the API call
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=contents,
                config=generation_config,
                system_instruction=system_instruction
            )

            # 3. Process response
            json_text = response.text
            if not json_text:
                st.error("Received an empty response from the API.")
                raise ValueError("Empty response text.")

            # 4. Parse the expected JSON structure
            try:
                parsed_results = json.loads(json_text)
                return parsed_results
            except json.JSONDecodeError:
                st.error(f"Failed to parse JSON response. Received: {json_text[:200]}...")
                raise ValueError("Invalid JSON format in response.")
        
        except APIError as e:
            st.error(f"API Error (Attempt {attempt + 1}/{max_retries}): {e.message}")
            if attempt < max_retries - 1:
                st.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2
            else:
                st.error("Final attempt failed. Please check your API key and quota.")
                return None
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            return None
    
    return None


# --- Streamlit UI Setup ---

# Custom styling for a cohesive RizenAi look
st.markdown(
    """
    <style>
    /* Global Background and Font */
    body { font-family: 'Poppins', sans-serif; }
    .stApp {
        background-color: #00243B; /* var(--bg-dark) */
        color: white;
    }
    
    /* Header and Title */
    h1 { color: white; }
    .neon-cyan { color: #00FFFF; }
    .neon-aqua { color: #00BFFF; }

    /* Input Fields (mimicking neon-input) */
    .stTextInput>div>div>input, 
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>div {
        background-color: rgba(0, 0, 0, 0.3); 
        border: 1px solid #00FFFF; /* var(--accent-cyan) */
        color: white !important;
        border-radius: 0.5rem;
        padding: 0.75rem;
    }

    /* Primary Button (mimicking neon-button) */
    .stButton>button {
        background: linear-gradient(145deg, #00BFFF, #00FFFF); /* accent-aqua to accent-cyan */
        color: #00243B !important; /* var(--bg-dark) */
        font-weight: 600;
        border-radius: 0.5rem;
        box-shadow: 
            0 4px 6px rgba(0, 0, 0, 0.4), 
            0 0 15px #00FFFF; /* accent-cyan */
        transition: all 0.2s ease;
        padding: 1rem 1.5rem;
        font-size: 1.125rem;
        width: 100%;
    }

    /* Output Card (mimicking neon-border) */
    .output-card {
        border: 2px solid transparent;
        background-clip: padding-box, border-box;
        background-origin: padding-box, border-box;
        background-image: linear-gradient(to bottom, #00243B, #00243B), 
                          linear-gradient(to right, #00FFFF, #FF00FF, #FFD700, #00FFFF);
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 0 10px rgba(0, 191, 255, 0.2);
    }
    </style>
    """, 
    unsafe_allow_html=True
)

# Header Section
st.title("RizenAi Content Repurposer")
st.markdown('<p class="text-xl text-gray-300">Turn one piece of older content into many</p>', unsafe_allow_html=True)
st.markdown('<p class="text-lg italic neon-cyan mb-8">“Good stories never die; They are just retold time and over again”</p>', unsafe_allow_html=True)

st.markdown('<h2 class="text-2xl font-semibold neon-aqua border-b border-cyan-500 pb-2">Your Blueprint (The Man-Machine Teaming Input)</h2>', unsafe_allow_html=True)


# --- Input Form ---
with st.form("repurpose_form"):
    
    # 1. Profile Details
    col1, col2 = st.columns(2)
    with col1:
        user_name = st.text_input("My Name", placeholder="Mandatory: e.g., Sudip", key="user-name")
    with col2:
        profession = st.text_input("My Profession (20 words max)", placeholder="Mandatory: e.g., Solopreneur Coach focused on time-freedom systems.", key="profession")

    # 2. Goals and Tone
    col3, col4 = st.columns(2)
    with col3:
        objective = st.selectbox(
            "Objective for Repurposing (e.g., Reach More People)",
            options=[
                "Reach More People (Audience Growth)",
                "Boost Engagement (Interaction)",
                "Promote a Specific Service/Product",
                "Build Authority/Thought Leadership"
            ],
            key="objective"
        )
    with col4:
        tone = st.selectbox(
            "Desired Tone & Style (e.g., Casual and Friendly)",
            options=[
                "Informative and Professional",
                "Casual and Friendly (Storytelling)",
                "Bold and Provocative",
                "Motivational and Encouraging"
            ],
            key="tone"
        )
        
    # 3. Target Platforms (using multiselect)
    platform_options = [
        "LinkedIn Post",
        "Twitter/X Thread",
        "Instagram Carousel Script",
        "Blog Intro Paragraph",
        "Email Newsletter Snippet"
    ]
    platforms = st.multiselect(
        "Target Platforms (Select multiple)",
        options=platform_options,
        default=["LinkedIn Post", "Twitter/X Thread"],
        key="platforms"
    )

    # 4. Original Content
    original_content = st.text_area(
        "Your Original Content (up to 200 words recommended)",
        height=200,
        placeholder="Mandatory: Paste your original article, transcript, or long-form content here. Example: 'When I started, I spent 8 hours on content creation. Now, I use AI systems to reduce that to 1 hour, giving me 7 hours back for client work. Here is how I set up my Time-Freedom System...'",
        key="original-content"
    )

    # 5. Extra Info
    extra_info = st.text_input(
        "Any Extra Vital Information (e.g., specific keywords, call to action)",
        placeholder="Optional: e.g., Primary CTA is 'Visit rizenai.co to download my free guide.'",
        key="extra-info"
    )

    submitted = st.form_submit_button("🚀 Plug & Play: Repurpose Content Now")

# --- Submission Handler ---

if submitted:
    # Basic validation
    if not user_name or not profession or not original_content or not platforms:
        st.error("Please fill in all mandatory fields (Name, Profession, Original Content, and select at least one Platform).")
    elif not client:
        st.error("Gemini Client is not available. Please ensure your GEMINI_API_KEY is correctly set.")
    else:
        # Construct data structure
        form_data = {
            "name": user_name,
            "profession": profession,
            "objective": objective,
            "tone": tone.split('(')[0].strip(), # Clean up tone for the prompt
            "platforms": platforms,
            "original_content": original_content,
            "extra_info": extra_info
        }

        with st.spinner("Order Received: Executing Multi-Phase Repurposing Workflow..."):
            
            # The actual API call happens here
            results = repurpose_content(form_data)

            if results:
                st.success("Meal Served! Your content is ready.")
                
                # --- Output Section ---
                st.markdown('<h2 class="text-2xl font-semibold neon-aqua border-b border-aqua-500 pb-2 mt-8">Your Deliverables (The Profit)</h2>', unsafe_allow_html=True)
                
                # Iterate through results and display them in styled cards
                for key, content in results.items():
                    # Convert JSON key (e.g., LinkedIn_Post) back to readable name (LinkedIn Post)
                    platform_name = key.replace('_', ' ')
                    
                    st.markdown(f'<div class="output-card">', unsafe_allow_html=True)
                    st.markdown(f'<h3 class="text-xl font-bold neon-aqua border-b border-aqua-600 pb-2 mb-3">{platform_name} Deliverable</h3>', unsafe_allow_html=True)
                    
                    # Use st.code or st.text_area for clear presentation and easy copying
                    st.text_area(f"Content for {platform_name}", value=content, height=300, label_visibility="collapsed")
                    
                    st.markdown('</div>', unsafe_allow_html=True)

                # Optional: Provide the full results as a downloadable JSON file
                st.download_button(
                    label="Download All Content as JSON",
                    data=json.dumps(results, indent=2),
                    file_name="rizenai_content_export.json",
                    mime="application/json",
                    key='download_json'
                )
            else:
                st.error("The content generation failed. Check the error messages above and ensure your API key is correct and working.")

# --- Footer ---
st.markdown(
    """
    <div style="text-align: center; margin-top: 3rem; color: #555;">
        <p>© RizenAi.Co | All Rights Reserved</p>
    </div>
    """,
    unsafe_allow_html=True
)
