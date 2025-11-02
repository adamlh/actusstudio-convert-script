import streamlit as st
import fitz
import tempfile
import os # <-- Must be here

# (Your extract_raw_text_from_pdf and format_screenplay_text functions here)

# --- STREAMLIT APP ---
st.title("🎬 PDF Screenplay Converter")
st.write("Upload your PDF script to convert it into a formatted text file.")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # 1. INITIALIZE VARIABLES HERE: This is the fix for the NameError!
    pdf_path = None
    
    try:
        # 2. Use a temporary file to allow fitz to read the file contents
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            pdf_path = tmp_file.name # If the script fails before this line, pdf_path is still None

        st.info(f"Processing file: **{uploaded_file.name}**")

        # (Rest of your processing logic: extract_raw_text_from_pdf, format_screenplay_text, download_button)
        
        # ... (rest of the try block) ...

    except Exception as e:
        st.error(f"An error occurred during processing: {e}")
        
    finally:
        # 3. Check if pdf_path was actually set before trying to unlink it
        # This prevents the NameError: pdf_path is None if the try block failed early.
        if pdf_path and os.path.exists(pdf_path):
            os.unlink(pdf_path)