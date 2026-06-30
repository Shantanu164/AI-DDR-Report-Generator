import os
import pdfplumber
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# -----------------------------
# LOAD API KEY
# -----------------------------
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

# -----------------------------
# PDF TEXT EXTRACTION
# -----------------------------
def extract_text(uploaded_file, max_chars=3000):
    text = ""

    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

        text = text.replace("\n", " ").strip()

        return text[:max_chars] if text else "Not Available"

    except Exception as e:
        return f"Error : {e}"


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="AI DDR Generator",
    page_icon="🏗",
    layout="wide"
)

# -----------------------------
# SIMPLE CSS
# -----------------------------
st.markdown("""
<style>

/* Generate Button */
.stButton > button{
    width:220px;
    height:50px;
    border-radius:10px;
    background:#0E4C92;
    color:white;
    font-size:17px;
}

/* Remove hover effect */
.stButton > button:hover {
    background-color: #0E4C92 !important;
    color: white !important;
    border: none !important;
}

/* Remove click/focus effect */
.stButton > button:focus,
.stButton > button:active {
    background-color: #0E4C92 !important;
    color: white !important;
    border: none !important;
    box-shadow: none !important;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.title("🤖 AI DDR Report Generator")

st.caption(
    "Generate Professional Detailed Defect Reports using AI"
)

st.divider()

# -----------------------------
# FILE UPLOAD
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    inspection_file = st.file_uploader(
        "📄 Inspection Report",
        type=["pdf"]
    )

with col2:
    thermal_file = st.file_uploader(
        "🌡 Thermal Report (Optional)",
        type=["pdf"]
    )

st.divider()

# -----------------------------
# BUTTON
# -----------------------------
col1, col2, col3 = st.columns([2,1,2])

with col2:
    generate = st.button("🚀 Generate DDR Report", use_container_width=True)

# -----------------------------
# REPORT GENERATION
# -----------------------------
if generate:

    if inspection_file is None:
        st.error("Please upload Inspection Report.")

    else:

        with st.spinner("Generating DDR Report..."):

            inspection_text = extract_text(inspection_file)

            thermal_text = (
                extract_text(thermal_file,1000)
                if thermal_file
                else "Not Available"
            )

            # -----------------------------
            # CONFIDENCE SCORE
            # -----------------------------
            confidence = 50

            if inspection_text != "Not Available":
                confidence += 30

            if thermal_text != "Not Available":
                confidence += 20

            # -----------------------------
            # PROMPT
            # -----------------------------
            prompt = f"""

You are an expert Civil Engineering Inspection Assistant.

Generate a professional Detailed Defect Report (DDR).

Inspection Data:

{inspection_text}

Thermal Data:

{thermal_text}

Rules:

- Do NOT assume missing information.
- If data is missing write "Not Available".
- Generate the report in professional format.

Include:

1. Executive Summary

2. Overview

3. Inspection Findings

4. Thermal Analysis

5. Defects Identified

6. Risk Assessment

7. Recommendations

Also include AI Confidence Score:
{confidence}%

"""

            # -----------------------------
            # GROQ API
            # -----------------------------
            response = client.chat.completions.create(

                model="openai/gpt-oss-120b",

                messages=[

                    {
                        "role":"system",
                        "content":"You generate professional engineering reports."
                    },

                    {
                        "role":"user",
                        "content":prompt
                    }

                ],

                temperature=0.3

            )

            result = response.choices[0].message.content

            final_output = f"""

# DETAILED DEFECT REPORT (DDR)

This report is generated using AI.

AI Confidence Score : {confidence}%

{result}

"""

# -----------------------------
# OUTPUT
# -----------------------------
            st.success("✅ Report Generated Successfully")

            st.metric(
                label="AI Confidence",
                value=f"{confidence}%"
            )

            with st.expander("📋 View Generated DDR Report", expanded=True):
                st.markdown(final_output)

            st.download_button(
                label="📥 Download DDR Report",
                data=final_output,
                file_name="DDR_Report.txt",
                mime="text/plain"
            )