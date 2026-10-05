import io
import re
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from fpdf import FPDF
from config import LOGO_PATH


def sanitize_text(text: str) -> str:
    """Removes non-standard typographic quotes, symbols, and artifacts."""
    if not text:
        return ""
    
    replacements = {
        '“': '"', '”': '"', '‘': "'", '’': "'",
        '–': '-', '—': '-', '…': '...', '•': '*'
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
        
    text = re.sub(r'[\r\t]', '', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Strip markdown bold asterisks
    return text.strip()


def format_docx(text: str, doc_type: str) -> bytes:
    """Generates a styled Microsoft Word document (.docx) with logo, formatting, and terms table."""
    doc = Document()
    
    # Page setup
    section = doc.sections[0]
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)
    
    # Set standard font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(11)
    
    # Header: Add Logo if available
    if Path(LOGO_PATH).exists():
        header_p = doc.add_paragraph()
        header_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = header_p.add_run()
        run.add_picture(str(LOGO_PATH), width=Inches(1.8))
        
    # Title
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_p.paragraph_format.space_before = Pt(12)
    title_p.paragraph_format.space_after = Pt(18)
    title_run = title_p.add_run(doc_type.upper())
    title_run.font.size = Pt(16)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(15, 23, 42)
    
    # Body Paragraphs
    clean_text = sanitize_text(text)
    paragraphs = clean_text.split('\n\n')
    
    for p_text in paragraphs:
        p_text = p_text.strip()
        if not p_text:
            continue
            
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.line_spacing = 1.15
        
        # Check if line looks like a header
        if re.match(r'^(?:[0-9]+\.|[A-Z\s]{4,}:)', p_text) or p_text.isupper():
            run = p.add_run(p_text)
            run.font.bold = True
            run.font.size = Pt(12)
        else:
            p.add_run(p_text)

    # Key Terms Summary Table
    doc.add_paragraph().paragraph_format.space_before = Pt(12)
    table_heading = doc.add_paragraph()
    th_run = table_heading.add_run("KEY AGREEMENT SUMMARY")
    th_run.font.bold = True
    th_run.font.size = Pt(12)
    
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Clause / Aspect"
    hdr_cells[1].text = "Summary Details"
    hdr_cells[0].paragraphs[0].runs[0].font.bold = True
    hdr_cells[1].paragraphs[0].runs[0].font.bold = True
    
    # Add document metadata rows
    row_data = [
        ("Document Class", doc_type),
        ("Status", "Fully Executed / Generated Draft"),
        ("Compliance Standard", "LegalEase AI Draft Standards")
    ]
    for key, val in row_data:
        row_cells = table.add_row().cells
        row_cells[0].text = key
        row_cells[1].text = val

    # Footer
    footer = section.footer
    footer_p = footer.paragraphs[0]
    footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_run = footer_p.add_run("LegalEase AI Generated Document • Confidential")
    footer_run.font.size = Pt(9)
    footer_run.font.italic = True
    footer_run.font.color.rgb = RGBColor(128, 128, 128)

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


class LegalPDF(FPDF):
    """Custom FPDF class supporting headers, footers, and logo rendering."""
    
    def header(self):
        if Path(LOGO_PATH).exists():
            try:
                self.image(str(LOGO_PATH), x=160, y=10, w=35)
            except Exception:
                pass
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, "CONFIDENTIAL & LEGAL DOCUMENT", ln=True, align="L")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"LegalEase AI • Page {self.page_no()}/{{nb}}", align="C")


def format_pdf(text: str, doc_type: str) -> bytes:
    """Generates a clean, branded PDF document."""
    pdf = LegalPDF(orientation='P', unit='mm', format='A4')
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    
    # Document Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 10, doc_type.upper(), ln=True, align="C")
    pdf.ln(5)
    
    # Document Content
    clean_text = sanitize_text(text)
    pdf.set_font("Helvetica", size=10)
    pdf.set_text_color(30, 41, 59)
    
    lines = clean_text.split('\n')
    for line in lines:
        line_str = line.strip()
        if not line_str:
            pdf.ln(3)
            continue
            
        # Bold section headers
        if re.match(r'^(?:[0-9]+\.|[A-Z\s]{4,}:)', line_str) or line_str.isupper():
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 6, line_str)
            pdf.set_font("Helvetica", size=10)
        else:
            pdf.multi_cell(0, 5, line_str)
            
    return bytes(pdf.output())


def format_html_preview(text: str) -> str:
    """Transforms raw legal text into a dark-themed HTML preview."""
    clean_text = sanitize_text(text)
    paragraphs = clean_text.split('\n\n')
    html_content = []
    
    for p in paragraphs:
        p_str = p.strip().replace('\n', '<br>')
        if re.match(r'^(?:[0-9]+\.|[A-Z\s]{4,}:)', p_str) or (p_str.isupper() and len(p_str) < 60):
            html_content.append(f"<h4 style='color: #60A5FA; margin-top: 16px; margin-bottom: 6px;'>{p_str}</h4>")
        else:
            html_content.append(f"<p style='color: #E2E8F0; line-height: 1.6; margin-bottom: 10px;'>{p_str}</p>")
            
    return "".join(html_content)