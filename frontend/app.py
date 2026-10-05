import streamlit as st
import requests
from pathlib import Path
import sys

# Ensure root folder is in python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import BACKEND_URL, LOGO_PATH
from utils.formatters import sanitize_text, format_docx, format_pdf, format_html_preview

# Page Configuration
st.set_page_config(page_title="LegalEase - AI Legal Generator", layout="wide")

# Custom CSS for UI polish
st.markdown("""
    <style>
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    .main-title {
        text-align: center;
        color: #38BDF8;
        font-family: 'Helvetica', sans-serif;
        font-weight: 700;
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        color: #94A3B8;
        font-size: 1.1rem;
        margin-bottom: 25px;
    }
    .stButton>button {
        background-color: #2563EB;
        color: white;
        border-radius: 6px;
        font-weight: 600;
        border: none;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
    }
    </style>
""", unsafe_allow_html=True)

# Logo & Header Layout
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if Path(LOGO_PATH).exists():
        st.image(str(LOGO_PATH), use_container_width=True)
    st.markdown("<h1 class='main-title'>LegalEase</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>AI-Powered Legal Document Generator</p>", unsafe_allow_html=True)

st.divider()

# Left & Right Columns for Controls and Preview
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("📋 Document Parameters")
    
    document_type = st.text_input(
        "Document Type", 
        value="Freelance Work Contract",
        placeholder="e.g. Non-Disclosure Agreement, Lease Agreement"
    )
    
    parties = st.text_area(
        "Parties Involved", 
        value="Jane Doe (Service Provider)\nTechNova Inc. (Client)",
        height=100
    )
    
    terms = st.text_area(
        "Terms & Conditions (Use semicolons for separate points)", 
        value="Payment to be made within 30 days of invoice;\nProvider agrees to deliver work by agreed deadline;\nConfidentiality must be maintained at all times;\nTermination requires 15 days written notice.",
        height=120
    )
    
    dates = st.text_input("Effective Date", value="October 15, 2026")
    
    generate_btn = st.button("✨ Generate Document", type="primary")

# Application Session State
if "generated_document" not in st.session_state:
    st.session_state.generated_document = ""

if generate_btn:
    if not document_type or not parties or not terms:
        st.error("Please fill in all mandatory fields!")
    else:
        with st.spinner("Drafting legal document using Gemini AI..."):
            try:
                payload = {
                    "document_type": document_type,
                    "parties": parties,
                    "terms": terms,
                    "dates": dates
                }
                response = requests.post(f"{BACKEND_URL}/generate", json=payload, timeout=60)
                
                if response.status_code == 200:
                    raw_text = response.json().get("document", "")
                    st.session_state.generated_document = sanitize_text(raw_text)
                    st.success("Document Generated Successfully!")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to backend server: {str(e)}")

with col_right:
    st.subheader("📄 Document Preview & Export")
    
    if st.session_state.generated_document:
        tab_preview, tab_edit = st.tabs(["👁️ Styled Preview", "✏️ Edit Text"])
        
        with tab_preview:
            html_rendered = format_html_preview(st.session_state.generated_document)
            st.markdown(
                f"<div style='background-color: #1E293B; padding: 20px; border-radius: 8px; max-height: 450px; overflow-y: auto; border: 1px solid #334155;'>"
                f"{html_rendered}"
                f"</div>", 
                unsafe_allow_html=True
            )
            
        with tab_edit:
            edited_text = st.text_area(
                "Modify the wording below:", 
                value=st.session_state.generated_document, 
                height=350
            )
            st.session_state.generated_document = edited_text

        st.markdown("### 📥 Download Options")
        d_col1, d_col2, d_col3 = st.columns(3)
        
        file_stub = document_type.lower().replace(" ", "_")
        
        with d_col1:
            st.download_button(
                label="📄 Download .TXT",
                data=st.session_state.generated_document,
                file_name=f"{file_stub}.txt",
                mime="text/plain"
            )
            
        with d_col2:
            docx_data = format_docx(st.session_state.generated_document, document_type)
            st.download_button(
                label="📝 Download .DOCX",
                data=docx_data,
                file_name=f"{file_stub}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
        with d_col3:
            pdf_data = format_pdf(st.session_state.generated_document, document_type)
            st.download_button(
                label="📕 Download .PDF",
                data=pdf_data,
                file_name=f"{file_stub}.pdf",
                mime="application/pdf"
            )
    else:
        st.info("Fill in the parameters on the left and click 'Generate Document' to see the preview here.")