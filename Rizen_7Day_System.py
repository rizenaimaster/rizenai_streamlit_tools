# app.py
"""
RizenAi — 7-Day Consistency Launchpad (Prototype #2)
Streamlit app implementing:
- Welcome / User Guide
- Inputs (niche, goal, style, platforms, time)
- Option: user topic OR AI topic finder
- Background "DAS" relevance check (placeholder LLM call)
- Present 3 Topic+Angle choices (radio)
- Step-by-step generation of 7 days content (Next)
- Execution docs (calendar, checklist, scorecard)
- Download .txt export
----------
REPLACE the placeholder `call_llm_*` functions with real LLM/Gemini API calls.
"""

import streamlit as st
from dataclasses import dataclass
from typing import List, Dict
import textwrap
import time
import json

# -------------------------
# UI helpers & styling
# -------------------------
st.set_page_config(page_title="RizenAi — 7-Day Consistency Launchpad", layout="centered")

CSS = """
<style>
body { background: linear-gradient(180deg, #0f1724 0%, #111827 70%); color: #e6eef6; }
.stButton>button { background-color: #00fff0; color: #051017; font-weight: 700; padding: 12px 18px; }
.card { background: rgba(8,10,12,0.55); border-radius: 12px; padding: 18px; margin-bottom: 12px; }
.small-muted { color: #9aaec3; font-size: 0.9rem; }
.h1 { font-weight:700; color: #00f0d6; }
.border-accent { border: 2px solid #00f0d6; border-radius: 12px; padding:14px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# -------------------------
# Session State init
# -------------------------
if "screen" not in st.session_state:
    st.session_state.screen = "welcome"  # welcome -> inputs -> choose_topic -> topic_opts -> generate_flow -> execution_docs -> done
if "user_inputs" not in st.session_state:
    st.session_state.user_inputs = {}
if "topic_options" not in st.session_state:
    st.session_state.topic_options = []  # list[dict{text,angle,score}]
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = None
if "day_index" not in st.session_state:
    st.session_state.day_index = 0
if "day_outputs" not in st.session_state:
    st.session_state.day_outputs = []
if "execution_docs" not in st.session_state:
    st.session_state.execution_docs = {}
if "das_result" not in st.session_state:
    st.session_state.das_result = None

# -------------------------
# Placeholder LLM functions - Replace with real implementation
# -------------------------
def call_llm_das_check(user_inputs: Dict, topic_text: str) -> Dict:
    """
    Replace with Gemini/LLM call that:
    - compares topic relevance with 'social media & content landscape as on 1 Dec 2025'
    - returns {'relevance': 'relevant'|'irrelevant', 'score': float, 'notes': str}
    For now we simulate.
    """
    # Simulated quick check: if topic contains 'travel' or 'marketing' give higher score
    text = (topic_text or "").lower()
    score = 0.6
    if any(k in text for k in ["travel", "marketing", "content", "startup", "business"]):
        score = 0.85
    elif len(text) < 6:
        score = 0.3
    notes = "Simulated DAS check. Replace call_llm_das_check with real LLM API call that uses 'social media & content landscape as on 1 Dec 2025'."
    relevance = "relevant" if score >= 0.5 else "irrelevant"
    return {"relevance": relevance, "score": score, "notes": notes}

def call_llm_generate_topics(user_inputs: Dict) -> List[Dict]:
    """
    Replace with LLM: produce 3 topic+angle options relevant to user inputs (use current trend prompt).
    Return list of dicts: {'topic': str, 'angle': str, 'rationale': str}
    """
    niche = user_inputs.get("niche","Creator")
    # Simulated
    return [
        {"topic": f"{niche} — Beginner's Checklist", "angle": "A practical, step-by-step checklist to start", "rationale": "High engagement; practical value"},
        {"topic": f"{niche} — Mistakes to avoid", "angle": "Top 5 mistakes+how to fix them", "rationale": "Shareable, quick wins"},
        {"topic": f"{niche} — Daily routine for results", "angle": "One-week routine to get measurable outcomes", "rationale": "Great for 7-day series"}
    ]

def call_llm_generate_day(user_inputs: Dict, topic: str, angle: str, day_number:int) -> Dict:
    """
    Replace with LLM: generate full script/caption/hook/CTA/hashtags for a given day.
    Return {'day': int, 'hook':str, 'script':str, 'cta':str, 'hashtags':List[str]}
    """
    # Simulated: a simple templated output
    hook = f"Day {day_number}: {angle} — quick hook for {topic}"
    script = f"{topic} — Day {day_number}\n\nThis is a concise script built in {user_inputs.get('tone','informal')} tone. Focus: {angle}.\n\nActionable tip: Do this for 3 mins..."
    cta = "Save & try this today. Tell me how it went!"
    hashtags = ["#consistency","#RizenAi","#content"]
    return {"day": day_number, "hook": hook, "script": script, "cta": cta, "hashtags": hashtags}

def call_llm_generate_execution_docs(user_inputs: Dict, topic: str, angle: str, day_outputs: List[Dict]) -> Dict:
    """
    Replace with LLM: produce calendar, checklist and scorecard text.
    Return {'calendar':str,'checklist':str,'scorecard':str}
    """
    cal_lines = []
    for d in day_outputs:
        cal_lines.append(f"Day {d['day']}: {d['hook'][:80]} - CTA: {d['cta']}")
    calendar = "Weekly Content Calendar\n" + "\n".join(cal_lines)
    checklist = "Posting Checklist:\n- Prepare visual\n- Schedule\n- Engage first hour\n- Save analytics"
    scorecard = "Consistency Scorecard: Post frequency, Engagement, Completion"
    return {"calendar":calendar,"checklist":checklist,"scorecard":scorecard}

# -------------------------
# Prompts (for developer) - what to send to Gemini (example)
# -------------------------
LLM_PROMPT_EXAMPLE_DAS = textwrap.dedent("""\
You are given:
- user_inputs: {user_inputs}
- candidate_topic: {topic}
Task:
1) Check social media & content landscape relevance as on 01-Dec-2025.
2) Score relevance 0..1 and state brief reasons.
3) If score < 0.5, suggest short alternative angle.
Return JSON: {{ "relevance":"relevant"|"irrelevant", "score":float, "notes":str }}
""")

LLM_PROMPT_EXAMPLE_TOPIC_GEN = textwrap.dedent("""\
You are a content strategist. Based on these user inputs: {user_inputs}
Produce exactly 3 Topic+Angle options. For each option give: topic, angle, 1-sentence rationale, and 1 micro-hashtag set.
Strict JSON output.
""")

LLM_PROMPT_EXAMPLE_DAY = textwrap.dedent("""\
You are a content writer. Inputs: {user_inputs}, chosen topic: {topic}, chosen angle: {angle}, day: {day}.
Produce: hook (single line), full script (max 220 words), CTA (short), 5 hashtags.
Return JSON.
""")

# -------------------------
# UI Screens
# -------------------------
def screen_welcome():
    st.markdown("<h1 class='h1'>More RizenAi systems — Coming Soon</h1>", unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### The 7-Day Consistency Launchpad")
    st.markdown("Turn your messy content life into a clean, consistent weekly system — starting today.")
    st.markdown('<div class="small-muted">Simple. Guided. One week at a time.</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("User Guide"):
            st.session_state.show_guide = True
            st.session_state.screen = "inputs"
    with col2:
        if st.button("Let's Begin"):
            st.session_state.screen = "inputs"

    if st.session_state.get("show_guide", False):
        st.markdown("---")
        st.markdown("**Quick guide:** This tool helps you pick one topic and run a frictionless 7-day series. The app will ask a few simple questions and then generate everything day-by-day. You can download the final pack as `.txt`.")
        st.markdown("---")

def screen_inputs():
    st.header("Step 1 — Tell me about you (quick)")
    with st.form("input_form"):
        niche = st.text_input("What do you want to talk about? (Niche / Industry)", value=st.session_state.user_inputs.get("niche",""))
        goal = st.selectbox("Goal", ["Grow brand","Attract clients","Share knowledge","Build authority"], index=0)
        style = st.selectbox("Tone / Style", ["Educator","Storyteller","Conversational","Entertaining","Witty"], index=0)
        platforms = st.multiselect("Platforms", ["LinkedIn","Instagram","Twitter/X","YouTube Short","Facebook"], default=["LinkedIn","Instagram"])
        time_per_day = st.selectbox("Time available per day", ["10 min","20 min","30 min","1 hour"], index=0)
        submitted = st.form_submit_button("Continue")

    if submitted:
        st.session_state.user_inputs = {
            "niche": niche.strip(),
            "goal": goal,
            "style": style,
            "platforms": platforms,
            "time_per_day": time_per_day
        }
        st.session_state.screen = "choose_topic"

def screen_choose_topic():
    st.header("Step 2 — Topic choice")
    st.markdown("Would you like to use a topic you already have, or let AI suggest a relevant topic?")
    choice = st.radio("", ("I have my own topic", "Let AI suggest topics"), index=1)

    if choice == "I have my own topic":
        topic = st.text_input("Enter your topic (one short sentence)", value=st.session_state.user_inputs.get("topic",""))
        if st.button("Check topic & continue"):
            st.session_state.user_inputs["topic"] = topic.strip()
            # run background DAS check
            st.session_state.das_result = call_llm_das_check(st.session_state.user_inputs, topic.strip())
            st.session_state.screen = "das_result"
    else:
        if st.button("Find best-fit topics (AI)"):
            st.session_state.topic_options = call_llm_generate_topics(st.session_state.user_inputs)
            st.session_state.screen = "topic_options"

def screen_das_result():
    st.header("Topic relevance — Background check (DAS simulation)")
    res = st.session_state.das_result or {"relevance":"irrelevant","score":0,"notes":"no data"}
    st.write(f"**Relevance:** {res['relevance'].upper()}   •   **Score:** {res['score']:.2f}")
    st.info(res["notes"])
    st.markdown("---")
    if res["relevance"] == "relevant":
        if st.button("Start my 7-day strategy with this topic"):
            # prepare topic options from user topic (angle=default)
            topic = st.session_state.user_inputs.get("topic","Untitled Topic")
            st.session_state.topic_options = [{"topic": topic, "angle": "Default angle: Practical series", "rationale": "User-provided topic"}]
            st.session_state.screen = "topic_options"
    else:
        st.warning("This topic appears less relevant according to current landscape checks.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Continue with my topic anyway"):
                topic = st.session_state.user_inputs.get("topic","Untitled Topic")
                st.session_state.topic_options = [{"topic": topic, "angle": "User angle", "rationale": "User chose to continue"}]
                st.session_state.screen = "topic_options"
        with col2:
            if st.button("Let AI suggest better options"):
                st.session_state.topic_options = call_llm_generate_topics(st.session_state.user_inputs)
                st.session_state.screen = "topic_options"

def screen_topic_options():
    st.header("Step 3 — Pick a Topic + Angle")
    st.markdown("Choose one option below. If you want a different mix, click 'Regenerate'.")
    for i, opt in enumerate(st.session_state.topic_options):
        st.markdown(f"**{i+1}. {opt['topic']}** — *{opt.get('angle','')}*")
        st.write(f"_{opt.get('rationale','')}_")
    selected = st.radio("Select", options=list(range(len(st.session_state.topic_options))), format_func=lambda i: f"Option {i+1}")
    if st.button("Start my 7-day strategy"):
        idx = selected
        pick = st.session_state.topic_options[idx]
        st.session_state.selected_topic = pick
        st.session_state.day_index = 0
        st.session_state.day_outputs = []
        st.session_state.screen = "generate_days"
    if st.button("Regenerate topics"):
        st.session_state.topic_options = call_llm_generate_topics(st.session_state.user_inputs)
        st.experimental_rerun()

def screen_generate_days():
    st.header("Step 4 — Generate your 7-day series (one day at a time)")
    pick = st.session_state.selected_topic
    if not pick:
        st.error("No topic selected, go back.")
        return
    st.markdown(f"**Topic:** {pick['topic']}  —  **Angle:** {pick['angle']}")
    st.markdown("Press **Generate Next Day** to create the next day's post. This app generates one day at a time to avoid overwhelming decisions and to keep the user in control.")

    if st.session_state.day_index >= 7:
        st.success("All 7 days generated.")
        if st.button("Generate Execution Docs (calendar, checklist, scorecard)"):
            st.session_state.execution_docs = call_llm_generate_execution_docs(st.session_state.user_inputs, pick['topic'], pick['angle'], st.session_state.day_outputs)
            st.session_state.screen = "execution_docs"
        return

    # show already generated days
    for d in st.session_state.day_outputs:
        st.markdown(f"**Day {d['day']}** — {d['hook']}")
        with st.expander("Show script & details"):
            st.write(d["script"])
            st.write("CTA:", d["cta"])
            st.write("Hashtags:", " ".join(d["hashtags"]))

    if st.button("Generate Next Day"):
        # call LLM to generate next day
        next_day = st.session_state.day_index + 1
        # show spinner while generating
        with st.spinner(f"Generating day {next_day}..."):
            out = call_llm_generate_day(st.session_state.user_inputs, pick['topic'], pick['angle'], next_day)
            # small delay to mimic LLM
            time.sleep(0.8)
            st.session_state.day_outputs.append(out)
            st.session_state.day_index += 1
            st.experimental_rerun()

def screen_execution_docs():
    st.header("Step 5 — Execution Pack (downloadable)")
    docs = st.session_state.execution_docs or {}
    st.subheader("Calendar")
    st.code(docs.get("calendar","(empty)"))
    st.subheader("Checklist")
    st.code(docs.get("checklist","(empty)"))
    st.subheader("Scorecard")
    st.code(docs.get("scorecard","(empty)"))

    # Build downloadable .txt
    downloadable = []
    downloadable.append("=== RizenAi 7-Day Consistency Launchpad ===")
    downloadable.append(f"Topic: {st.session_state.selected_topic['topic']}")
    downloadable.append(f"Angle: {st.session_state.selected_topic['angle']}")
    downloadable.append("\n---\n7 Day Outputs\n")
    for d in st.session_state.day_outputs:
        downloadable.append(f"Day {d['day']}\nHOOK: {d['hook']}\nSCRIPT:\n{d['script']}\nCTA: {d['cta']}\nHASHTAGS: {' '.join(d['hashtags'])}\n---\n")
    downloadable.append("\n---\nEXECUTION DOCS\n")
    downloadable.append(docs.get("calendar",""))
    downloadable.append("\n")
    downloadable.append(docs.get("checklist",""))
    downloadable.append("\n")
    downloadable.append(docs.get("scorecard",""))

    txt_blob = "\n".join(downloadable)
    st.download_button("Download your 7-Day Pack (.txt)", txt_blob, file_name="Week_X_Content_Pack.txt", mime="text/plain")

    st.markdown("---")
    if st.button("Start another plan"):
        # reset core session state except some user inputs
        st.session_state.topic_options = []
        st.session_state.selected_topic = None
        st.session_state.day_index = 0
        st.session_state.day_outputs = []
        st.session_state.execution_docs = {}
        st.session_state.screen = "choose_topic"

# -------------------------
# Router
# -------------------------
def router():
    screen = st.session_state.screen
    if screen == "welcome":
        screen_welcome()
    elif screen == "inputs":
        screen_inputs()
    elif screen == "choose_topic":
        screen_choose_topic()
    elif screen == "das_result":
        screen_das_result()
    elif screen == "topic_options":
        screen_topic_options()
    elif screen == "generate_days":
        screen_generate_days()
    elif screen == "execution_docs":
        screen_execution_docs()
    else:
        st.write("Unknown screen")

router()

# -------------------------
# Footer / small help UI
# -------------------------
st.markdown("---")
with st.expander("Quick terms & help (i-button)"):
    st.markdown("""
**Identity**: the micro-content identity we create to keep your voice consistent across the week.  
**Hook**: one-line attention-grabbing opener.  
**CTA**: a single action you want the reader/viewer to take.  
**Hashtags**: optional; used for discoverability but treat as suggestions.  
**DAS**: background relevance check against the 'social landscape as on 1 Dec 2025'. The production LLM must make this check.  
""")
