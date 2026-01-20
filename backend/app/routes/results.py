"""
Results route handlers for displaying analysis results.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .config import results_store, TEMPLATES_DIR
from .utils import format_state_for_display

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def load_result(workflow_id: str) -> dict:
    """Load result from in-memory store only (no file I/O)."""
    if workflow_id in results_store:
        return results_store[workflow_id]
    raise HTTPException(status_code=404, detail="Workflow result not found")


@router.get("/results/{workflow_id}", response_class=HTMLResponse)
async def results_page(request: Request, workflow_id: str):
    """
    Display the analysis results in HTML format.
    
    Args:
        request: FastAPI request object
        workflow_id: Unique workflow identifier
        
    Returns:
        HTML template response with formatted results
        
    Raises:
        HTTPException: If result not found
    """
    state = load_result(workflow_id)
    formatted_state = format_state_for_display(state)
    
    return templates.TemplateResponse("results.html", {
        "request": request,
        "state": formatted_state
    })


@router.get("/api/results/{workflow_id}")
async def get_results_api(workflow_id: str):
    """
    Get results as JSON (API endpoint).
    
    Args:
        workflow_id: Unique workflow identifier
        
    Returns:
        JSON response with raw workflow result
        
    Raises:
        HTTPException: If result not found
    """
    return load_result(workflow_id)
