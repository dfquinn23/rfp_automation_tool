# ui_streamlit.py

# ui_streamlit.py (Final, Cleaned Version)

import streamlit as st
import requests
from tempfile import NamedTemporaryFile
from run_pipeline import run_pipeline
from core.embed import embed_final_rfp
import os
import shutil

# --- Page Configuration ---
st.set_page_config(page_title="RFP Automation Tool", layout="centered")

# Your custom CSS styles can be placed here if you have any.
# st.markdown("""<style>...</style>""", unsafe_allow_html=True)


# --- UI Application Starts Here ---

st.image("fulllogo_transparent_nobuffer.png", width=200)

# Define paths used by the app
PAST_RFPS_DIR = "past_rfps"
OUTPUT_DIR = "output"

st.title("📄 RFP Draft Assistant")


# --- Sidebar Navigation ---
page = st.sidebar.selectbox(
    "Navigation", ["Process New RFP", "View Past RFPs"])


# --- Page 1: Process New RFP ---
if page == "Process New RFP":

    st.header("1. Generate Draft from New RFP")
    uploaded_file = st.file_uploader(
        "Upload a .docx RFP file", type="docx", key="new_rfp_upload")

    if uploaded_file:
        # Use a temporary file to safely handle the upload
        with NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name

        if st.button("Generate Draft Responses", type="primary"):
            with st.spinner("Analyzing document and searching database... This may take a few minutes."):
                try:
                    run_pipeline(tmp_path)
                    st.success("✅ Draft Generation Complete!")

                    # Provide download links for the generated documents
                    full_draft_path = os.path.join(
                        OUTPUT_DIR, "generated_rfp_draft.docx")
                    if os.path.exists(full_draft_path):
                        with open(full_draft_path, "rb") as f:
                            st.download_button(
                                "⬇️ Download Full Draft", f, file_name="generated_rfp_draft.docx"
                            )

                    review_draft_path = os.path.join(
                        OUTPUT_DIR, "low_confidence_rfp_draft.docx")
                    if os.path.exists(review_draft_path):
                        with open(review_draft_path, "rb") as f:
                            st.download_button(
                                "⬇️ Download Low-Confidence Draft", f, file_name="low_confidence_rfp_draft.docx"
                            )
                except Exception as e:
                    st.error(f"❌ An error occurred during processing: {e}")
                finally:
                    # Securely clean up the temporary file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

    st.markdown("---")  # Visual separator

    st.header("2. Archive a Finalized RFP")
    st.write(
        "Upload a final, human-reviewed RFP to add it to the knowledge base for future searches.")
    final_uploaded_file = st.file_uploader(
        "Upload your final .docx draft", type="docx", key="final_rfp_upload")

    if final_uploaded_file:
        with NamedTemporaryFile(delete=False, suffix=".docx") as final_tmp:
            final_tmp.write(final_uploaded_file.getbuffer())
            final_tmp_path = final_tmp.name

        if st.button("Add to Knowledge Base"):
            with st.spinner("Vectorizing and saving final draft..."):
                try:
                    embed_final_rfp(final_tmp_path)
                    st.success(
                        "🧠 Final RFP added to the Qdrant knowledge base successfully!")

                    # Also save a copy to the local archive folder
                    os.makedirs(PAST_RFPS_DIR, exist_ok=True)
                    final_save_path = os.path.join(
                        PAST_RFPS_DIR, final_uploaded_file.name)
                    shutil.copy(final_tmp_path, final_save_path)
                    st.info(
                        f"✅ Copied final draft to local '{PAST_RFPS_DIR}' folder.")
                except Exception as e:
                    st.error(f"❌ Error during final draft processing: {e}")
                finally:
                    if os.path.exists(final_tmp_path):
                        os.unlink(final_tmp_path)


# --- Page 2: View Past RFPs ---
elif page == "View Past RFPs":

    st.header("🗂️ Past RFPs Archive")
    st.write("Download previously archived RFP documents.")

    os.makedirs(PAST_RFPS_DIR, exist_ok=True)
    rfp_files = [f for f in os.listdir(PAST_RFPS_DIR) if f.endswith(".docx")]

    if not rfp_files:
        st.info(
            f"No archived RFPs found in the '{PAST_RFPS_DIR}' directory yet.")
    else:
        for rfp_file in rfp_files:
            rfp_path = os.path.join(PAST_RFPS_DIR, rfp_file)
            with open(rfp_path, "rb") as f:
                st.download_button(
                    f"⬇️ Download {rfp_file}", f, file_name=rfp_file
                )
# Your n8n Cloud webhook URL for the 'new_draft_ready' trigger.
N8N_WEBHOOK_URL = "https://dfq23.app.n8n.cloud/webhook/5177ed66-1297-48d6-979a-6c7232559cbd"


def trigger_new_draft_notification(data_to_send=None):
    """
    Triggers the 'New Draft Ready' n8n workflow with an optional data payload.

    Args:
        data_to_send (dict, optional): A dictionary of data to send to the workflow.
                                     This is useful for personalizing emails.
                                     Defaults to None.

    Returns:
        bool: True if the webhook was triggered successfully, False otherwise.
    """
    try:
        # Send the data to your n8n webhook
        response = requests.post(N8N_WEBHOOK_URL, json=data_to_send)

        # This will raise an exception for bad responses (like 404 or 500)
        response.raise_for_status()

        st.success("Successfully notified the team that a new draft is ready!")
        return True

    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while triggering the notification: {e}")
        return False

# --- Example of how to use this in your Streamlit app ---


st.title("Document Collaboration Tool")

st.write("When the draft is prepared and ready for review, click the button below.")

if st.button("Notify Team: New Draft is Ready"):
    # You can customize the data you send to n8n here.
    # This data will be available in your n8n workflow to use in emails,
    # Slack messages, etc.
    draft_details = {
        "document_name": "New RFP Completed",
        "author": "Dan Quinn",
        "status": "Ready for Review",
        "version": "1.0"
    }

    # Call the function to trigger the webhook
    trigger_new_draft_notification(draft_details)

# # LOCAL ONLY
# # ui_streamlit.py
# import requests
# import streamlit as st
# from tempfile import NamedTemporaryFile
# from run_pipeline import run_pipeline
# from core.embed import embed_final_rfp
# import os
# import shutil

# # Styling for dark theme + white labels
# st.set_page_config(page_title="RFP Automation Tool", layout="centered")
# st.markdown(
#     """
#     <style>
#     @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

#     .stApp {
#         background-color: #0A2540;
#         color: white;
#         font-family: 'Roboto', sans-serif;
#     }

#     h1, h2, h3, h4, h5, h6,
#     .stMarkdown,
#     .css-10trblm,  /* general text */
#     label,
#     .st-b8, .st-c2, .st-ca {
#         color: white !important;
#         font-family: 'Roboto', sans-serif !important;
#     }

#     /* Sidebar styling */
#     section[data-testid="stSidebar"] {
#         background-color: #071a30 !important;
#         color: white !important;
#     }

#     /* File drop zone background and text */
#     section[data-testid="stFileDropzone"] {
#         background-color: #1a2e44 !important;
#         color: white !important;
#         border: 1px solid #3c6f91 !important;
#         border-radius: 6px !important;
#     }

#     section[data-testid="stFileDropzone"] * {
#         color: white !important;
#         font-family: 'Roboto', sans-serif !important;
#     }

#     /* Input fields */
#     .stTextInput > div > div > input {
#         background-color: #ffffff20;
#         color: white;
#         font-family: 'Roboto', sans-serif;
#     }

#     /* Buttons */
#     .stButton > button {
#         background-color: #1f77b4;
#         color: white;
#         border-radius: 5px;
#         font-family: 'Roboto', sans-serif;
#     }

#     /* Uploaded file name */
#     .uploadedFileName, .stUploadedFile {
#         color: white !important;
#     }
#     /* Fix download button text color */
#     .stDownloadButton > button {
#     color: #0A2540 !important;  /* dark blue text */
#     font-weight: 600;
# }

# .stDownloadButton > button, .stDownloadButton > button > div {
#     text-align: left !important;
#     justify-content: flex-start !important;
#     display: flex !important;
#     padding-left: 16px;
# }


# /* Uniform width for all download buttons */
#     .stDownloadButton > button {
#     width: 750px !important;
#     text-align: left;
#     padding-left: 16px;
# }

# /* Sidebar dropdown (selectbox) text color fix */
#     section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
#     font-family: 'Roboto', sans-serif !important, color: #0A2540 !important;  /* dark blue */
# }
# /* Fix sidebar selectbox dropdown list items (when open) */
# div[data-baseweb="popover"] ul {
#     background-color: white !important;
# }

# div[data-baseweb="popover"] li {
#     color: #0A2540 !important;  /* dark blue text */
#     font-family: 'Roboto', sans-serif !important;
# }


#     </style>
#     """,
#     unsafe_allow_html=True
# )


# # Add logo (optional)
# # old:  st.image("C:\\Users\\Daniel Quinn\\Desktop\\AI_Consultancy_Project\\rfp_assistant\\rfp_automation_tool\\fulllogo_transparent_nobuffer.png", width=200)
# st.image("fulllogo_transparent_nobuffer.png", width=200)

# # Paths
# NEW_RFPS_DIR = "new_rfps"
# PAST_RFPS_DIR = "past_rfps"
# OUTPUT_DIR = "output"

# st.title("\U0001F4C4 RFP Draft Assistant")

# # Sidebar navigation
# page = st.sidebar.selectbox("Navigation", ["Upload New RFP", "View Past RFPs"])

# if page == "Upload New RFP":
#     st.header("\U0001F4E4 Upload a New RFP")

#     uploaded_file = st.file_uploader("Upload a .docx RFP file", type="docx")

#     if uploaded_file is not None:
#         with NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
#             tmp.write(uploaded_file.getbuffer())
#             tmp_path = tmp.name

#         if st.button("Generate Draft Responses"):
#             with st.spinner("Running pipeline. This may take a few minutes..."):
#                 try:
#                     run_pipeline(tmp_path)
#                     st.success("✅ Draft Generation Complete!")

#                     try:
#                         requests.post(
#                             "http://localhost:5678/webhook/new_draft_ready",
#                             json={
#                                 "filename": "generated_rfp_draft.docx",
#                                 "filepath": os.path.abspath("output/generated_rfp_draft.docx")
#                             }
#                         )
#                         st.info("📧 Reviewer notification sent via n8n.")
#                     except Exception as e:
#                         st.warning(f"⚠ Could not notify reviewers: {e}")

#                     with open("output/generated_rfp_draft.docx", "rb") as f:
#                         st.download_button(
#                             "⬇ Download Full Draft", f, file_name="generated_rfp_draft.docx")

#                     review_path = "output/low_confidence_rfp_draft.docx"
#                     if os.path.exists(review_path):
#                         with open(review_path, "rb") as f:
#                             st.download_button(
#                                 "⚠ Download Low-Confidence Draft", f, file_name="low_confidence_rfp_draft.docx")

#                 except Exception as e:
#                     st.error(f"❌ Error during processing: {e}")

#     st.header("✅ Upload Final Draft for Archiving and Vectorization")

#     final_uploaded_file = st.file_uploader(
#         "Upload your final reviewed RFP draft (.docx)", type="docx", key="final")

#     if final_uploaded_file is not None:
#         with NamedTemporaryFile(delete=False, suffix=".docx") as final_tmp:
#             final_tmp.write(final_uploaded_file.getbuffer())
#             final_tmp_path = final_tmp.name

#         if st.button("Embed and Save Final Draft"):
#             with st.spinner("Embedding final draft and saving..."):
#                 try:
#                     embed_final_rfp(final_tmp_path)
#                     st.success("🧠 Final RFP embedded to Qdrant successfully!")

#                     # Save final file to past_rfps
#                     os.makedirs(PAST_RFPS_DIR, exist_ok=True)
#                     final_save_path = os.path.join(
#                         PAST_RFPS_DIR, final_uploaded_file.name)
#                     shutil.copy(final_tmp_path, final_save_path)
#                     st.success(f"✅ Final draft saved to '{final_save_path}'")

#                     try:
#                         requests.post(
#                             "http://localhost:5678/webhook/final_rfp_ready",
#                             json={
#                                 "filename": final_uploaded_file.name,
#                                 "filepath": os.path.abspath(final_save_path)
#                             }
#                         )
#                         st.info("📧 Final RFP notification sent via n8n.")
#                     except Exception as e:
#                         st.warning(
#                             f"⚠ Could not notify final RFP recipients: {e}")

#                 except Exception as e:
#                     st.error(f"❌ Error during final draft processing: {e}")

# elif page == "View Past RFPs":
#     st.header("🗂️ Past RFPs Archive")

#     rfp_files = [f for f in os.listdir(PAST_RFPS_DIR) if f.endswith(".docx")]

#     if not rfp_files:
#         st.info("No archived RFPs found yet.")
#     else:
#         for rfp_file in rfp_files:
#             rfp_path = os.path.join(PAST_RFPS_DIR, rfp_file)
#             with open(rfp_path, "rb") as f:
#                 st.download_button(
#                     f"⬇ Download {rfp_file}", f, file_name=rfp_file)
