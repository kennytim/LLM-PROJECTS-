
import streamlit as st
import tempfile
from support import init_chain, analyze_pdf_lab_report

st.set_page_config(page_title="Lab Test Interpreter", page_icon="🧪")
st.title("🧪 Lab Test Interpreter")

chain = init_chain()

uploaded_file = st.file_uploader("Upload your lab test PDF", type=["pdf"])

if uploaded_file is not None:
    # Save uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getbuffer())
        tmp_pdf_path = tmp_file.name

    # Now pass the real temp file path to your analyzer
    with st.spinner("🔍 Analyzing your report..."):
        try:
            summary = analyze_pdf_lab_report(tmp_pdf_path, chain)
            st.success("✅ Analysis complete!")
            with st.expander("📋 Summary of Results"):
                st.write(summary)
        except Exception as e:
            st.error(f"❌ Error analyzing PDF: {e}")
else:
    st.info("Please upload a PDF file to start analysis.")

import streamlit.components.v1 as components

st.metric(label="Hemoglobin", value="12 g/dL", delta="-2 below normal")
st.metric(label="Cholesterol", value="220 mg/dL", delta="+20 above normal")

st.markdown("---")
st.caption("Built with ❤️ using Streamlit & LangChain by Kehinde Fagbayibo")





