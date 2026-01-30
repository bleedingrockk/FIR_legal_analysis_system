from tavily import TavilyClient
from pydantic import BaseModel, Field
from app.langgraph.state import WorkflowState
from app.models.openai import llm_model
import logging
import os

logger = logging.getLogger(__name__)

# Initialize Tavily client with API key from environment
tavily_api_key = os.getenv("TAVILY_API_KEY", "")
client = TavilyClient(tavily_api_key)
    
class Question(BaseModel):
    question: str = Field(description="Question that I can search on the internet to find historical cases related to the given FIR")
    
def historical_cases(state: WorkflowState) -> dict:
    """
    Search for historical cases related to the FIR and return summarized results.
    """
    logger.info("Starting historical cases search")
    
    if not state.get("pdf_content_in_english"):
        raise ValueError("pdf_content_in_english is required for historical cases search")
    
    pdf_content = state["pdf_content_in_english"]
    logger.debug(f"FIR content length: {len(pdf_content)} characters")

    # Generate search question based on FIR content
    # Limit to first 2000 chars to avoid token limits
    truncated_content = pdf_content[:5000] if len(pdf_content) > 2000 else pdf_content
    prompt = f"""Based on the following FIR content, form 1 question that I can search on the internet to find historical cases related to this FIR.

FIR Content:
{truncated_content}

Generate a specific search question that will help find similar historical legal cases."""
    
    question = llm_model.with_structured_output(Question).invoke(prompt)
    logger.info(f"Generated search question: {question.question}")
    
    # Search using Tavily
    response = client.search(
        query=question.question,
        search_depth="advanced",
        include_usage=True,
        max_results=5,
        include_raw_content=True
    )
    
    # Process results: keep title, url, raw_content and summarize raw_content
    historical_cases_list = []
    
    # Handle both dict and object responses from Tavily
    results = response.get('results', []) if isinstance(response, dict) else response.results
    
    for result in results:
        # Handle both dict and object result formats
        if isinstance(result, dict):
            title = result.get('title', '')
            url = result.get('url', '')
            raw_content = result.get('raw_content', '') or ''
        else:
            title = result.title
            url = result.url
            raw_content = result.raw_content if hasattr(result, 'raw_content') and result.raw_content else ""
        
        # Summarize raw_content using LLM
        summary = ""
        if raw_content:
            # Limit content to avoid token limits
            truncated_raw = raw_content[:3000] if len(raw_content) > 3000 else raw_content
            summary_prompt = f"""Summarize the following legal case content in 2-3 sentences, focusing on key facts, legal issues, and outcomes:

{truncated_raw}"""
            
            try:
                summary_response = llm_model.invoke(summary_prompt)
                summary = summary_response.content if hasattr(summary_response, 'content') else str(summary_response)
                logger.debug(f"Summarized case: {title}")
            except Exception as e:
                logger.error(f"Error summarizing case {title}: {e}")
                summary = "Summary unavailable"
        
        case_data = {
            "title": title,
            "url": url,
            "summary": summary
        }
        historical_cases_list.append(case_data)
    
    logger.info(f"Found {len(historical_cases_list)} historical cases")
    
    return {
        "historical_cases": historical_cases_list
    }