import os
import shutil
import tempfile
import json
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.models.trade_schemas import LetterOfCredit, VerificationReport, Incoterm
from app.agents.langgraph_workflow import TradeFinanceLangGraph

app = FastAPI(
    title="Global Trade Finance & UCP 600 AI Verification Service",
    description="Agentic Multi-Agent UCP 600 Document Examination Engine powered by LangGraph",
    version="1.0.0"
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instrument Prometheus Metrics (/metrics)
Instrumentator().instrument(app).expose(app)

# Initialize the LangGraph Engine
workflow_engine = TradeFinanceLangGraph()

@app.get("/health")
def health_check():
    return {
        "status": "UP",
        "service": "ai-agent-service",
        "framework": "LangGraph + FastAPI",
        "rules_engine": "UCP 600 / ISBP 745"
    }

@app.post(
    "/api/v1/verify-documents",
    response_model=VerificationReport,
    summary="Upload Trade PDFs and Execute Autonomous UCP 600 Examination"
)
async def verify_trade_documents(
    lc_payload: str = Form(..., description="JSON string of LetterOfCredit model"),
    presentation_reference: str = Form(..., description="Unique trade presentation ID"),
    bill_of_lading: Optional[UploadFile] = File(None),
    commercial_invoice: Optional[UploadFile] = File(None),
    packing_list: Optional[UploadFile] = File(None),
    insurance_certificate: Optional[UploadFile] = File(None)
):
    try:
        lc_dict = json.loads(lc_payload)
        lc = LetterOfCredit(**lc_dict)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid LC payload JSON: {str(e)}"
        )

    # Save uploaded files temporarily for OCR extraction
    temp_dir = tempfile.mkdtemp(prefix="trade_doc_")
    pdf_paths = {}

    try:
        if bill_of_lading:
            bl_path = os.path.join(temp_dir, f"bl_{bill_of_lading.filename}")
            with open(bl_path, "wb") as f:
                shutil.copyfileobj(bill_of_lading.file, f)
            pdf_paths["bl"] = bl_path

        if commercial_invoice:
            inv_path = os.path.join(temp_dir, f"inv_{commercial_invoice.filename}")
            with open(inv_path, "wb") as f:
                shutil.copyfileobj(commercial_invoice.file, f)
            pdf_paths["invoice"] = inv_path

        if packing_list:
            pl_path = os.path.join(temp_dir, f"pl_{packing_list.filename}")
            with open(pl_path, "wb") as f:
                shutil.copyfileobj(packing_list.file, f)
            pdf_paths["packing_list"] = pl_path

        if insurance_certificate:
            ins_path = os.path.join(temp_dir, f"ins_{insurance_certificate.filename}")
            with open(ins_path, "wb") as f:
                shutil.copyfileobj(insurance_certificate.file, f)
            pdf_paths["insurance"] = ins_path

        # Run the full LangGraph verification pipeline
        report = workflow_engine.verify(
            lc=lc,
            presentation_ref=presentation_reference,
            pdf_paths=pdf_paths
        )

        return report

    finally:
        # Clean up temporary storage
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
