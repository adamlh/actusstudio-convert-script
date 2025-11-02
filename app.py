import streamlit as st
import fitz # PyMuPDF - ensure this is installable on your host
# import tempfile
# import os

# (Paste your extract_raw_text_from_pdf and format_screenplay_text functions here)

# --- STREAMLIT APP ---
st.title("🎬 PDF Screenplay Converter")
st.write("Upload your PDF script to convert it into a formatted text file.")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # 1. Save the uploaded file temporarily
    # In a real app, you'd save it to a temp file/location for fitz to read
    # Since fitz requires a file path, we'll use a temp file.
    
    try:
        # Use a temporary file to allow fitz to read the file contents
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            pdf_path = tmp_file.name

        st.info(f"Processing file: **{uploaded_file.name}**")

        # Step 1: Extract Text
        raw_script_text = extract_raw_text_from_pdf(pdf_path)

        if raw_script_text:
            # Step 2: Format Script
            formatted_script = format_screenplay_text(raw_script_text)

            # Step 3: Offer the result for download
            st.success("Conversion Complete!")
            
            st.download_button(
                label="📥 Download Formatted Script (.txt)",
                data=formatted_script,
                file_name=f"formatted_{uploaded_file.name.replace('.pdf', '.txt')}",
                mime="text/plain"
            )

            st.subheader("Formatted Script Preview:")
            st.code(formatted_script[:5000], language='text') # Show a preview

        else:
            st.error("Could not extract text from the PDF. Please check the file.")
            
    except Exception as e:
        st.error(f"An error occurred during processing: {e}")
        
    finally:
        # Clean up the temporary file
        os.unlink(pdf_path)