# ui_streamlit.py

import numpy as np
from qdrant_client import models
from core.search import get_qdrant_client
import requests
import streamlit as st
from tempfile import NamedTemporaryFile
from run_pipeline import run_pipeline
from core.embed import embed_final_rfp
import os
import shutil

# ===================================================================
# ================= TEMPORARY DEBUGGING CODE ========================
# ===================================================================
# Place this right after your imports at the top of ui_streamlit.py

st.subheader("🕵️‍♂️ Debugging Info")
st.write("The Streamlit app is currently using these secrets:")
try:
    # Attempt to read the secrets
    url_from_secrets = st.secrets.get("QDRANT_CLUSTER_URL", "SECRET NOT FOUND")
    key_from_secrets = st.secrets.get("QDRANT_API_KEY", "SECRET NOT FOUND")

    # For security, we'll only display a portion of the key
    if key_from_secrets != "SECRET NOT FOUND" and len(key_from_secrets) > 8:
        key_display = f"Starts with '{key_from_secrets[:4]}', Ends with '{key_from_secrets[-4:]}'"
    else:
        key_display = "SECRET NOT FOUND or key is too short"

    # Display the credentials the app is using
    st.info(f"**Cluster URL:** `{url_from_secrets}`")
    st.warning(f"**API Key:** `{key_display}`")

except Exception as e:
    st.error(f"An error occurred while trying to read secrets: {e}")

st.divider()

# ===================================================================
# ================= NEW: "WRITE TEST" CODE ==========================
# ===================================================================
# Place this block right after the first one

st.subheader("✍️ Qdrant Write Test")


# Get the client using the cached function from your search.py
client = get_qdrant_client()

if client:
    TEST_COLLECTION_NAME = "streamlit-write-test"
    st.write(
        f"Attempting to create/write to a test collection named: `{TEST_COLLECTION_NAME}`")
    try:
        # 1. Attempt to create a test collection. Using recreate_collection is easiest for a test.
        client.recreate_collection(
            collection_name=TEST_COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=4, distance=models.Distance.DOT)  # Small, simple vector
        )
        st.success("✅ Step 1: Successfully CREATED the test collection.")

        # 2. Attempt to upsert a single point into the new collection
        client.upsert(
            collection_name=TEST_COLLECTION_NAME,
            points=[
                models.PointStruct(id=1, vector=np.random.rand(
                    4).tolist(), payload={"test": "success"})
            ],
            wait=True
        )
        st.success(
            "✅ Step 2: Successfully WROTE a point into the test collection.")

        st.balloons()
        st.info("🎉 CONCLUSION: The Write Test was successful! This means the Streamlit app has full read/write permissions for your Qdrant cluster.")

    except Exception as e:
        st.error("❌ CONCLUSION: The Write Test FAILED.")
        st.write("The app was unable to write to your Qdrant cluster. This could indicate a permissions issue with the API key.")
        # This will print the full technical error details below
        st.exception(e)
else:
    st.error("Could not get a Qdrant client for the write test.")

st.divider()
# ===================================================================
# ================= END OF "WRITE TEST" CODE ========================
# ===================================================================
# ===================================================================
# ================= END OF DEBUGGING CODE ===========================
# ===================================================================


# ... the rest of your ui_streamlit.py code starts here

# Styling for dark theme + white labels
st.set_page_config(page_title="RFP Automation Tool", layout="centered")
st.markdown("""
<style>
/* Custom CSS omitted for brevity */
</style>
""", unsafe_allow_html=True)

# Add logo (optional)
st.image("fulllogo_transparent_nobuffer.png", width=200)

# Paths
NEW_RFPS_DIR = "new_rfps"
PAST_RFPS_DIR = "past_rfps"
OUTPUT_DIR = "output"

st.title("\U0001F4C4 RFP Draft Assistant")

# Sidebar navigation
page = st.sidebar.selectbox("Navigation", ["Upload New RFP", "View Past RFPs"])

if page == "Upload New RFP":
    st.header("\U0001F4E4 Upload a New RFP")
    uploaded_file = st.file_uploader("Upload a .docx RFP file", type="docx")

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
                        st.download_button(
                            "⬇ Download Full Draft", f, file_name="generated_rfp_draft.docx")

                    review_path = "output/low_confidence_rfp_draft.docx"
                    if os.path.exists(review_path):
                        with open(review_path, "rb") as f:
                            st.download_button(
                                "⚠ Download Low-Confidence Draft", f, file_name="low_confidence_rfp_draft.docx")

                except Exception as e:
                    st.error(f"❌ Error during processing: {e}")

    st.header("✅ Upload Final Draft for Archiving and Vectorization")
    final_uploaded_file = st.file_uploader(
        "Upload your final reviewed RFP draft (.docx)", type="docx", key="final")

    if final_uploaded_file is not None:
        with NamedTemporaryFile(delete=False, suffix=".docx") as final_tmp:
            final_tmp.write(final_uploaded_file.getbuffer())
            final_tmp_path = final_tmp.name

        if st.button("Embed and Save Final Draft"):
            with st.spinner("Embedding final draft and saving..."):
                try:
                    embed_final_rfp(final_tmp_path)
                    st.success("🧠 Final RFP embedded to Qdrant successfully!")

                    os.makedirs(PAST_RFPS_DIR, exist_ok=True)
                    final_save_path = os.path.join(
                        PAST_RFPS_DIR, final_uploaded_file.name)
                    shutil.copy(final_tmp_path, final_save_path)
                    st.success(f"✅ Final draft saved to '{final_save_path}'")

                except Exception as e:
                    st.error(f"❌ Error during final draft processing: {e}")

elif page == "View Past RFPs":
    st.header("🗂️ Past RFPs Archive")
    rfp_files = [f for f in os.listdir(PAST_RFPS_DIR) if f.endswith(".docx")]

    if not rfp_files:
        st.info("No archived RFPs found yet.")
    else:
        for rfp_file in rfp_files:
            rfp_path = os.path.join(PAST_RFPS_DIR, rfp_file)
            with open(rfp_path, "rb") as f:
                st.download_button(
                    f"⬇ Download {rfp_file}", f, file_name=rfp_file)


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
