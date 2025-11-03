import streamlit as st
import fitz # PyMuPDF
import tempfile
import os
import sys
from werkzeug.utils import secure_filename

# =================================================================
# Core PDF Conversion Functions
# =================================================================

def extract_raw_text_from_pdf(pdf_path):
    """Extracts raw text from a PDF."""
    try:
        doc = fitz.open(pdf_path)
        full_text = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            # Use 'text' output for basic text extraction
            text = page.get_text("text") 
            full_text.append(text)
        
        doc.close()
        raw_output = "\n\n--- PAGE BREAK ---\n\n".join(full_text)
        return raw_output
    
    except Exception as e:
        # Print error to Streamlit logs for debugging
        print(f"🚨 ERROR: Failed during PDF extraction: {e}", file=sys.stderr)
        return ""

def format_screenplay_text(raw_text):
    """Applies formatting heuristics to raw script text."""
    if not raw_text:
        return ""

    lines = raw_text.split('\n')
    formatted_script = []
    
    # Define Indentations
    CHARACTER_INDENT = " " * 30
    PARENTHETICAL_INDENT = " " * 24
    DIALOGUE_INDENT = " " * 18
    
    is_dialogue_block = False
    
    for line in lines:
        # Clean up whitespace
        line = ' '.join(line.split()).strip() 
        
        if not line or '--- PAGE BREAK ---' in line:
            continue
        
        line_upper = line.upper()

        # 1. SCENE HEADING (Slugline)
        if line_upper.startswith('INT.') or line_upper.startswith('EXT.'):
            formatted_script.append(f"\n{line_upper}\n")
            is_dialogue_block = False
        
        # 2. CHARACTER CUE
        elif len(line) < 35 and line_upper == line and line.count('.') < 2 and not line_upper.endswith(('TO', 'OUT', 'END')):
            if '(' in line and ')' in line:
                # Handle dual names or descriptors in character line
                char_name, ext = line.rsplit('(', 1)
                formatted_script.append(f"{CHARACTER_INDENT}{char_name.strip()} ({ext}\n")
            else:
                formatted_script.append(f"{CHARACTER_INDENT}{line}\n")
            is_dialogue_block = True
        
        # 3. PARENTHETICAL
        elif line.startswith('(') and line.endswith(')'):
            formatted_script.append(f"{PARENTHETICAL_INDENT}{line}\n")
            is_dialogue_block = True
            
        # 4. DIALOGUE
        elif is_dialogue_block:
            formatted_script.append(f"{DIALOGUE_INDENT}{line}\n")
        
        # 5. TRANSITION
        elif line_upper == 'THE END' or line_upper.endswith('TO:') or line_upper.endswith('OUT'):
            formatted_script.append(f"\n{' ' * 60}{line_upper}\n")
            is_dialogue_block = False
            
        # 6. ACTION (Default fallback)
        else:
            formatted_script.append(f"{line}\n")
            is_dialogue_block = False

    return "\n".join(formatted_script)


# =================================================================
# Streamlit Application Interface
# =================================================================

st.set_page_config(page_title="🎬 PDF Script Converter")
st.title("🎬 PDF Script Converter")
st.write("Upload your PDF script to convert it into a formatted plain text file.")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Initialize pdf_path here to prevent NameError in finally block
    pdf_path = None
    output_path = None

    try:
        st.info(f"Processing file: **{secure_filename(uploaded_file.name)}**...")

        # 1. Save the uploaded file to a temporary location for fitz to read
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            pdf_path = tmp_file.name

        # 2. Process the file
        raw_script_text = extract_raw_text_from_pdf(pdf_path)

        if raw_script_text.strip():
            # 3. Format the script text
            formatted_script = format_screenplay_text(raw_script_text)

            # 4. Save the result to a temporary TXT file
            output_filename = f"formatted_{secure_filename(uploaded_file.name).replace('.pdf', '.txt')}"
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as out_file:
                # Write the output as UTF-8 bytes for the download button
                out_file.write(formatted_script.encode("utf-8"))
                output_path = out_file.name
            
            # 5. Offer the result for download
            st.success("Conversion Complete! Download your file below.")
            
            with open(output_path, "rb") as f:
                st.download_button(
                    label="📥 Download Formatted Script (.txt)",
                    data=f,
                    file_name=output_filename,
                    mime="text/plain"
                )

            st.subheader("Formatted Script Preview (First 2000 Lines):")
            # Show a preview of the first few lines
            st.code('\n'.join(formatted_script.split('\n')[:2000]), language='text')

        else:
            st.error("Could not extract any meaningful text from the PDF. Check if the PDF content is text-based.")
            
    except Exception as e:
        # Catch and display any remaining errors
        st.error(f"An unexpected error occurred during processing: {e}")
        st.exception(e)

    finally:
        # 6. Clean up temporary files, ensuring they were defined and exist
        if pdf_path and os.path.exists(pdf_path):
            os.unlink(pdf_path)
        if output_path and os.path.exists(output_path):
            os.unlink(output_path)