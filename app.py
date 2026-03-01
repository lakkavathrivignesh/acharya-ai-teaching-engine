import streamlit as st
from google import genai
import json
import os

# ================== CONFIG ==================

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ================== GLOBAL STYLING ==================

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to right, #eef2f3, #d9e2ec);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ================== BRAND HEADER ==================

st.markdown(
    """
    <div style='text-align:center;
                padding:35px 20px;
                background: linear-gradient(135deg, #4a90e2, #9013fe);
                border-radius:20px;
                color:white;
                margin-bottom:30px;
                box-shadow:0 10px 25px rgba(0,0,0,0.25);'>
        <h1 style='margin:0;font-size:42px;'>ACHARYA</h1>
        <p style='margin:8px 0 0 0;font-size:18px;opacity:0.9;'>
            Adaptive AI Teaching Engine
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ================== SESSION STATE ==================

if "stage" not in st.session_state:
    st.session_state.stage = 0
if "lesson" not in st.session_state:
    st.session_state.lesson = None
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "teaching_style" not in st.session_state:
    st.session_state.teaching_style = None
if "slide_index" not in st.session_state:
    st.session_state.slide_index = 0
if "socratic_step" not in st.session_state:
    st.session_state.socratic_step = 0
if "socratic_data" not in st.session_state:
    st.session_state.socratic_data = None

progress_map = {0: 0.33, 1: 0.66, 2: 1.0}
st.progress(progress_map.get(st.session_state.stage, 0))

# ================== STAGE 0 ==================

if st.session_state.stage == 0:

    st.markdown("## 📘 Lesson")

    if st.session_state.lesson is None:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Explain Newton's First Law clearly in under 120 words."
        )
        st.session_state.lesson = response.text

    st.markdown(
        f"<div style='padding:25px;border-radius:20px;background:white;'>{st.session_state.lesson}</div>",
        unsafe_allow_html=True
    )

    if st.button("🚀 Start Assessment"):
        st.session_state.stage = 1
        st.rerun()

# ================== STAGE 1 ==================

elif st.session_state.stage == 1:

    student_answer = st.text_area(
        "Why do passengers move forward when a car suddenly stops?"
    )

    if st.button("Analyze My Understanding"):

        analysis_prompt = f"""
        Analyze this answer about Newton's First Law.

        Student Answer:
        {student_answer}

        Decide:
        1) understanding_level → confused | partial | surface | deep
        2) recommended_style → socratic | adaptive

        Return ONLY JSON.
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=analysis_prompt
        )

        raw = response.text.strip()
        start = raw.find("{")
        end = raw.rfind("}")
        analysis = json.loads(raw[start:end+1])

        st.session_state.analysis = analysis
        st.session_state.teaching_style = analysis["recommended_style"].capitalize()
        st.session_state.stage = 2
        st.rerun()

# ================== STAGE 2 ==================

elif st.session_state.stage == 2:

    level = st.session_state.analysis["understanding_level"]
    style = st.session_state.teaching_style

    if style == "Socratic":
        st.markdown("## 🧠 Socratic Interactive Mode")
        st.write("Interactive reasoning mode activated.")
    else:
        st.markdown("## 📊 Adaptive Explanation")
        st.write(f"Student level detected: {level}")