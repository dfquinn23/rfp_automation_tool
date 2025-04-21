import streamlit as st
from tempfile import NamedTemporaryFile
from run_pipeline import run_pipeline
import os

st.set_page_config(page_title="RFP Automation Tool", layout="centered")
st.title("📄 RFP Draft Assistant")
st.markdown(
    "Upload a new RFP document to generate draft responses using your existing RFP library.")

uploaded_file = st.file_uploader("Upload a .docx RTFP file", type="docx")

if uploaded_file is not None:
    with NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(uploaded_file.getbuffer())
        tmp_path = tmp.name

    if st.button("Generate Draft Responses"):
        with st.spinner("Running pipeline. This may take a few minutes..."):
            try:
                run_pipeline(tmp_path)
                st.success("✅ Draft Generation Complete!")

                with open("output/generated_rfp_draft.docx", "rb") as f:
                    st.download_button("⬇ Download Full Draft",
                                       f, file_name="generated_rfp_draft.docx")

                review_path = "output/low_confidence_rfp_draft_docx"
                if os.path.exists(review_path):
                    with open(review_path, "rb") as f:
                        st.download_button(
                            "⚠ Download Low-Confidence Draft", f, file_name="low_confidence_rfp_draft.docx")

            except Exception as e:
                st.error(f"❌ Error During Processing: {e}")
