from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from ai_core.gemini_generator import GeminiDocumentGenerator

router = APIRouter()
generator = GeminiDocumentGenerator()

class DocumentRequest(BaseModel):
    document_type: str = Field(..., example="Employment Contract")
    parties: str = Field(..., example="Employer: TechCorp Inc.\nEmployee: Jane Doe")
    terms: str = Field(..., example="Salary: $120,000/yr; Notice period: 30 days")
    dates: str = Field(..., example="October 15, 2026")

@router.post("/generate")
async def generate_legal_document(request: DocumentRequest):
    """API endpoint to receive contract details and invoke Gemini Generator."""
    try:
        document_text = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            dates=request.dates
        )
        return {"status": "success", "document": document_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document generation failed: {str(e)}")