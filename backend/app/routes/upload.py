"""
Upload route handlers for FIR PDF processing.
"""

import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.langgraph.workflow import graph
from .config import results_store, TEMPLATES_DIR

# Initialize router
router = APIRouter()

# Setup templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/", response_class=HTMLResponse)
async def upload_page(request: Request):
    """
    Render the PDF upload page.
    
    Args:
        request: FastAPI request object
        
    Returns:
        HTML template response
    """
    return templates.TemplateResponse("upload.html", {"request": request})


@router.post("/upload")
async def upload_pdf(
    request: Request,
    file: UploadFile = File(...)
):
    """
    Upload and process a FIR PDF file.
    
    Args:
        request: FastAPI request object
        file: Uploaded PDF file
        
    Returns:
        JSON response with workflow_id and redirect URL
        
    Raises:
        HTTPException: If file is not PDF or processing fails
    """
    # Validate file type
    if not file.filename or not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400, 
            detail="Only PDF files are allowed"
        )
    
    # Generate unique workflow ID
    workflow_id = str(uuid.uuid4())

    # Read file into memory (no disk save)
    try:
        pdf_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

    try:
        graph_state = {
            "pdf_bytes": pdf_bytes,
            "pdf_filename": file.filename or "document.pdf",
        }

        print(f"🚀 Starting workflow execution for {workflow_id}...")
        result = graph.invoke(graph_state)

        result["workflow_id"] = workflow_id
        result["pdf_filename"] = file.filename or "document.pdf"

        # Drop pdf_bytes before storing (keep in-memory only, no persistence)
        result = {k: v for k, v in result.items() if k != "pdf_bytes"}

        results_store[workflow_id] = result

        print(f"✅ Workflow completed for {workflow_id}")

        return JSONResponse({
            "success": True,
            "workflow_id": workflow_id,
            "redirect_url": f"/results/{workflow_id}",
        })
    except Exception as e:
        print(f"❌ Error processing PDF for {workflow_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
