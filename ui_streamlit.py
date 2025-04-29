# ui_streamlit.py
import streamlit as st
from tempfile import NamedTemporaryFile
from run_pipeline import run_pipeline
import os
from scripts.notify_n8n import notify_n8n  # ✅ Unified placement
from core.embed import embed_final_rfp  # ✅ New: embedding final RFPs

st.set_page_config(page_title="RFP Automation Tool", layout="centered")
st.title("📄 RFP Draft Assistant")
st.markdown(
    "Use the tool below to generate RFP drafts and finalize reviewed documents.")

# --- Section 1: Upload New RFP for Draft Generation ---
st.header("🆕 Generate New Draft Responses")

uploaded_file = st.file_uploader(
    "Upload a .docx RFP file", type="docx", key="new_rfp")

if uploaded_file is not None:
    with NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(uploaded_file.getbuffer())
        tmp_path = tmp.name

    if st.button("Generate Draft Responses"):
        with st.spinner("Running pipeline. This may take a few minutes..."):
            try:
                run_pipeline(tmp_path)
                st.success("✅ Draft Generation Complete!")

                # Notify n8n about draft ready
                notify_n8n(filename=uploaded_file.name, client="Client XYZ")

                # Allow download
                with open("output/generated_rfp_draft.docx", "rb") as f:
                    st.download_button("⬇ Download Full Draft",
                                       f, file_name="generated_rfp_draft.docx")

                review_path = "output/low_confidence_rfp_draft.docx"
                if os.path.exists(review_path):
                    with open(review_path, "rb") as f:
                        st.download_button(
                            "⚠ Download Low-Confidence Draft", f, file_name="low_confidence_rfp_draft.docx")

            except Exception as e:
                st.error(f"❌ Error During Draft Generation: {e}")

st.divider()

# --- Section 2: Upload Final Approved RFP ---
st.header("✅ Upload Final Reviewed RFP")

final_rfp_file = st.file_uploader(
    "Upload the final .docx RFP file", type="docx", key="final_rfp")

if final_rfp_file is not None:
    final_save_path = os.path.join("past_rfps", final_rfp_file.name)
    with open(final_save_path, "wb") as f:
        f.write(final_rfp_file.getbuffer())

    st.success(f"✅ Final draft saved to past_rfps/{final_rfp_file.name}")

    # Notify n8n about final draft
    notify_n8n(filename=final_rfp_file.name,
               client="Client XYZ", event="final_draft_uploaded")

    # Embed the final RFP into Qdrant
    try:
        embed_final_rfp(final_save_path)
        st.success("🧠 Final RFP embedded to Qdrant successfully!")
    except Exception as e:
        st.error(f"❌ Error during embedding final RFP: {e}")
