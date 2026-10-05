import google.generativeai as genai
from config import GEMINI_API_KEY

class GeminiDocumentGenerator:
    """Handles AI-powered legal document creation using Google Gemini API."""
    
    def __init__(self, model_name: str = "gemini-1.5-pro"):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is missing!")
        
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(model_name)

    def generate_document(self, document_type: str, parties: str, terms: str, dates: str) -> str:
        """Constructs a structured prompt and generates legal agreement text."""
        prompt = (
            f"You are an expert legal counsel drafting a formal legal document.\n"
            f"Generate a professional, fully-detailed {document_type}.\n\n"
            f"DOCUMENT DETAILS:\n"
            f"- Document Type: {document_type}\n"
            f"- Effective Date: {dates}\n"
            f"- Parties Involved:\n{parties}\n\n"
            f"- Specific Clauses and Terms:\n{terms}\n\n"
            f"INSTRUCTIONS:\n"
            f"1. Structure the document with clear Title, Recitals, Definitions, Detailed Sections/Clauses, Term & Termination, Governing Law, and Signature Blocks.\n"
            f"2. Use formal legal language and precise terminology.\n"
            f"3. Explicitly incorporate all requested parties, terms, and dates into appropriate clauses.\n"
            f"4. Format section headings using clean plain text headers (e.g. '1. DEFINITIONS', '2. OBLIGATIONS').\n"
            f"5. Do NOT include markdown bold stars or unnecessary backticks. Keep the formatting clean for direct export.\n"
        )
        
        response = self.model.generate_content(prompt)
        return response.text