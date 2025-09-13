
from support import init_chain, analyze_pdf_lab_report
import streamlit as st
st.set_page_config(page_title="Lab Test Interpreter", page_icon="🧪", layout="wide")
st.title("🧪 Lab Test Interpreter")
st.markdown("Upload your **lab test report** (PDF or text) and get an easy-to-understand summary.")

chain = init_chain()  # do this once, maybe at top-level or in session state

uploaded_file = st.file_uploader("📂 Upload Lab Test Report", type=["pdf", "txt"])
if uploaded_file:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

with st.spinner("🔍 Analyzing your report..."):
    summary = analyze_pdf_lab_report("temp.pdf", chain)
st.success("✅ Analysis complete!")

with st.expander("📋 Summary of Results"):
    st.write(summary)

import streamlit.components.v1 as components

st.metric(label="Hemoglobin", value="12 g/dL", delta="-2 below normal")
st.metric(label="Cholesterol", value="220 mg/dL", delta="+20 above normal")

st.markdown("---")
st.caption("Built with ❤️ using Streamlit & LangChain by Kehinde Fagbayibo")


