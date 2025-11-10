# ui_streamlit.py
# Production-ready Streamlit UI with database management

import streamlit as st
from tempfile import NamedTemporaryFile
from run_pipeline import run_pipeline
from core.embed import embed_final_rfp, ensure_correct_collection
from core.search import get_qdrant_client
import os
import shutil
from pathlib import Path

# Page Configuration
st.set_page_config(
    page_title="RFP Automation Tool",
    page_icon="📄",
    layout="centered"
)

# Display logo if it exists
if os.path.exists("fulllogo_transparent_nobuffer.png"):
    st.image("fulllogo_transparent_nobuffer.png", width=200)

# Define paths
PAST_RFPS_DIR = "past_rfps"
OUTPUT_DIR = "output"

# Ensure directories exist
os.makedirs(PAST_RFPS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Main Title
st.title("📄 RFP Draft Assistant")
st.markdown("---")

# Sidebar Navigation
page = st.sidebar.selectbox(
    "Navigation",
    ["Process New RFP", "Archive Finalized RFP", "View Past RFPs", "Database Management"]
)

# ============================================================================
# PAGE 1: Process New RFP
# ============================================================================
if page == "Process New RFP":
    st.header("Generate Draft from New RFP")
    st.write("Upload a new RFP document and generate draft responses based on past answers.")
    
    uploaded_file = st.file_uploader(
        "Upload a .docx RFP file",
        type="docx",
        key="new_rfp_upload"
    )

    if uploaded_file:
        with NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name

        if st.button("Generate Draft Responses", type="primary"):
            with st.spinner("Analyzing document and searching database... This may take a few minutes."):
                try:
                    run_pipeline(tmp_path)
                    st.success("✅ Draft Generation Complete!")

                    # Provide download links
                    full_draft_path = os.path.join(OUTPUT_DIR, "generated_rfp_draft.docx")
                    if os.path.exists(full_draft_path):
                        with open(full_draft_path, "rb") as f:
                            st.download_button(
                                "⬇️ Download Full Draft",
                                f,
                                file_name="generated_rfp_draft.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )

                    review_draft_path = os.path.join(OUTPUT_DIR, "low_confidence_rfp_draft.docx")
                    if os.path.exists(review_draft_path):
                        with open(review_draft_path, "rb") as f:
                            st.download_button(
                                "⚠️ Download Low-Confidence Draft (Needs Review)",
                                f,
                                file_name="low_confidence_rfp_draft.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                            
                except Exception as e:
                    st.error(f"❌ An error occurred during processing: {str(e)}")
                    st.info("Please check that your Qdrant database is properly configured.")
                finally:
                    # Clean up temporary file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

# ============================================================================
# PAGE 2: Archive Finalized RFP
# ============================================================================
elif page == "Archive Finalized RFP":
    st.header("Archive a Finalized RFP")
    st.write(
        "Upload a finalized, human-reviewed RFP to add it to the knowledge base. "
        "This will extract question-answer pairs and make them searchable for future RFPs."
    )
    
    st.info(
        "📋 **Document Format**: Ensure your document has questions ending with '?' "
        "followed immediately by their answers in the next paragraph."
    )
    
    final_uploaded_file = st.file_uploader(
        "Upload your final .docx draft",
        type="docx",
        key="final_rfp_upload"
    )

    if final_uploaded_file:
        with NamedTemporaryFile(delete=False, suffix=".docx") as final_tmp:
            final_tmp.write(final_uploaded_file.getbuffer())
            final_tmp_path = final_tmp.name

        if st.button("Add to Knowledge Base", type="primary"):
            with st.spinner("Extracting Q&A pairs and adding to database..."):
                try:
                    # Embed and upload to Qdrant
                    embed_final_rfp(final_tmp_path)
                    st.success("🧠 Final RFP added to the Qdrant knowledge base successfully!")

                    # Save a copy to the local archive folder
                    final_save_path = os.path.join(PAST_RFPS_DIR, final_uploaded_file.name)
                    shutil.copy(final_tmp_path, final_save_path)
                    st.info(f"✅ Saved copy to '{PAST_RFPS_DIR}' folder for records.")
                    
                except Exception as e:
                    st.error(f"❌ Error during processing: {str(e)}")
                finally:
                    if os.path.exists(final_tmp_path):
                        os.unlink(final_tmp_path)

# ============================================================================
# PAGE 3: View Past RFPs
# ============================================================================
elif page == "View Past RFPs":
    st.header("🗂️ Past RFPs Archive")
    st.write("Download previously archived RFP documents.")

    rfp_files = sorted([f for f in os.listdir(PAST_RFPS_DIR) if f.endswith(".docx")])

    if not rfp_files:
        st.info(f"No archived RFPs found in the '{PAST_RFPS_DIR}' directory yet.")
        st.write("Upload finalized RFPs using the 'Archive Finalized RFP' page to build your archive.")
    else:
        st.write(f"**{len(rfp_files)} document(s) in archive:**")
        st.markdown("---")
        
        for rfp_file in rfp_files:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📄 {rfp_file}")
            with col2:
                rfp_path = os.path.join(PAST_RFPS_DIR, rfp_file)
                with open(rfp_path, "rb") as f:
                    st.download_button(
                        "Download",
                        f,
                        file_name=rfp_file,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key=f"download_{rfp_file}"
                    )

# ============================================================================
# PAGE 4: Database Management
# ============================================================================
elif page == "Database Management":
    st.header("🔧 Database Management")
    st.write("Manage your Qdrant vector database and rebuild it with clean data.")
    
    # Check Qdrant connection status
    client = get_qdrant_client()
    if client:
        st.success("✅ Connected to Qdrant database")
        
        try:
            collections = client.get_collections()
            collection_name = st.secrets.get("COLLECTION_NAME", "past_rfp_answers")
            
            collection_exists = any(c.name == collection_name for c in collections.collections)
            
            if collection_exists:
                st.info(f"📊 Collection '{collection_name}' exists")
                
                # Get collection info
                collection_info = client.get_collection(collection_name)
                st.write(f"**Points in database:** {collection_info.points_count}")
                st.write(f"**Vector dimensions:** {collection_info.config.params.vectors.size}")
            else:
                st.warning(f"⚠️ Collection '{collection_name}' does not exist")
                
        except Exception as e:
            st.error(f"Error checking database: {e}")
    else:
        st.error("❌ Cannot connect to Qdrant database")
        st.write("Please check your Streamlit secrets configuration.")
    
    st.markdown("---")
    
    # Database Rebuild Section
    st.subheader("🔄 Rebuild Database")
    st.write(
        "This will delete all existing data and re-embed all documents from your archive "
        "with proper Q&A extraction. Use this to clean up your database."
    )
    
    st.warning(
        "⚠️ **Warning**: This action will delete all existing vectors in your database. "
        "Make sure you have all important documents saved in the 'past_rfps/' folder."
    )
    
    # Count available documents
    rfp_count = len([f for f in os.listdir(PAST_RFPS_DIR) if f.endswith(".docx")])
    st.info(f"📄 Found {rfp_count} document(s) in '{PAST_RFPS_DIR}' folder to process")
    
    if rfp_count == 0:
        st.warning("No documents to process. Upload some finalized RFPs first.")
    else:
        # Confirmation checkbox
        confirm = st.checkbox(
            "I understand this will delete all existing database content and rebuild it",
            key="rebuild_confirm"
        )
        
        if st.button("Rebuild Database", type="primary", disabled=not confirm):
            with st.spinner("Rebuilding database... This may take several minutes."):
                try:
                    # Step 1: Recreate collection
                    st.write("🔄 Step 1: Recreating collection...")
                    ensure_correct_collection()
                    st.success("✅ Collection recreated")
                    
                    # Step 2: Process all documents
                    st.write(f"🔄 Step 2: Processing {rfp_count} document(s)...")
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    doc_paths = sorted(Path(PAST_RFPS_DIR).glob("*.docx"))
                    success_count = 0
                    error_count = 0
                    
                    for idx, doc_path in enumerate(doc_paths, 1):
                        status_text.write(f"Processing {idx}/{rfp_count}: {doc_path.name}")
                        
                        try:
                            embed_final_rfp(str(doc_path))
                            success_count += 1
                            st.write(f"✅ Processed: {doc_path.name}")
                        except Exception as e:
                            error_count += 1
                            st.error(f"❌ Failed: {doc_path.name} - {str(e)}")
                        
                        progress_bar.progress(idx / rfp_count)
                    
                    status_text.write("✅ Database rebuild complete!")
                    
                    # Summary
                    st.success(
                        f"🎉 Rebuild complete! Successfully processed {success_count}/{rfp_count} documents."
                    )
                    
                    if error_count > 0:
                        st.warning(f"⚠️ {error_count} document(s) failed. Check the errors above.")
                    
                except Exception as e:
                    st.error(f"❌ Database rebuild failed: {str(e)}")
                    st.write("Please check your configuration and try again.")

# ============================================================================
# Sidebar Information
# ============================================================================
st.sidebar.markdown("---")
st.sidebar.subheader("ℹ️ About")
st.sidebar.write(
    "This tool helps automate RFP responses by learning from past submissions. "
    "Upload new RFPs to generate draft answers, then archive finalized versions "
    "to improve future responses."
)
