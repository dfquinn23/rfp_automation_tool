import streamlit as st
from tempfile import NamedTemporaryFile
from run_pipeline import run_pipeline
from scripts.notify_n8n import notify_n8n
import os

st.set_page_config(page_title="RFP Automation Tool", layout="centered")
st.title("📄 RFP Draft Assistant")
st.markdown(
    "Upload a new RFP document to generate draft responses using your existing RFP library.")

uploaded_file = st.file_uploader("Upload a .docx RFP file", type="docx")

if uploaded_file is not None:
    # Save temp file (for local pipeline execution)
    with NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(uploaded_file.getbuffer())
        tmp_path = tmp.name

    # ✅ Save a copy into new_rfps/ for n8n to access
    permanent_path = os.path.join("new_rfps", uploaded_file.name)
    with open(permanent_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("Generate Draft Responses"):
        with st.spinner("Running pipeline. This may take a few minutes..."):
            try:
                run_pipeline(tmp_path)
                filename = uploaded_file.name
                client_name = "Client XYZ"  # You could add a field to capture this

                st.success("✅ Draft Generation Complete!")

                # Trigger webhook notification
                st.info("📤 Sending notification to n8n...")
                notify_n8n(filename=filename, client=client_name)
                st.success("✅ Notification sent to n8n!")

                # Download links
                full_path = "output/generated_rfp_draft.docx"
                if os.path.exists(full_path):
                    with open(full_path, "rb") as f:
                        st.download_button(
                            "⬇ Download Full Draft", f, file_name="generated_rfp_draft.docx")

                review_path = "output/low_confidence_rfp_draft.docx"
                if os.path.exists(review_path):
                    with open(review_path, "rb") as f:
                        st.download_button(
                            "⚠ Download Low-Confidence Draft", f, file_name="low_confidence_rfp_draft.docx")

            except Exception as e:
                st.error(f"❌ Error During Processing: {e}")
