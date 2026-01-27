from pydantic import BaseModel, Field
from app.langgraph.state import WorkflowState
from app.models.openai import llm_model
from typing import List
from app.utils.retry import exponential_backoff_retry
import logging
import json

logger = logging.getLogger(__name__)

class DosAndDonts(BaseModel):
    """Complete dos and donts for law enforcement officers"""
    dos: List[str] = Field(
        description="The dos officers should keep in mind while investigating the case or handling the evidence or the convict",
        max_length=10
    )
    donts: List[str] = Field(
        description="The donts officers should avoid while investigating the case or handling the evidence or the convict",
        max_length=10
    )

def format_sections(sections: List[dict] | None) -> str:
    """Format list of section dictionaries into readable text"""
    if not sections:
        return "None"
    
    formatted = []
    for section in sections:
        # Assuming sections have 'section' and 'description' or similar keys
        # Adjust based on your actual structure
        section_text = f"- {section.get('section', 'Unknown')}: {section.get('description', section.get('text', ''))}"
        formatted.append(section_text)
    
    return "\n".join(formatted)

def generate_dos_and_donts(state: WorkflowState) -> dict:
    """
    Generate comprehensive dos and donts from FIR content and forensic guidelines.
    """
    logger.info("Starting dos and donts generation")
    
    if not state.get("pdf_content_in_english"):
        raise ValueError("pdf_content_in_english is required for dos and donts generation")
    
    pdf_content = state["pdf_content_in_english"]
    ndps_sections_mapped = state.get("ndps_sections_mapped", [])
    bns_sections_mapped = state.get("bns_sections_mapped", [])
    bnss_sections_mapped = state.get("bnss_sections_mapped", [])
    bsa_sections_mapped = state.get("bsa_sections_mapped", [])
    forensic_guidelines_mapped = state.get("forensic_guidelines_mapped", [])
    
    # Format sections properly for LLM
    ndps_text = format_sections(ndps_sections_mapped)
    bns_text = format_sections(bns_sections_mapped)
    bnss_text = format_sections(bnss_sections_mapped)
    bsa_text = format_sections(bsa_sections_mapped)
    forensic_text = format_sections(forensic_guidelines_mapped)
    
    # Construct content for LLM
    content_for_llm = f"""Based on the following FIR content and legal sections, generate comprehensive dos and donts for law enforcement officers:

FIR Content:
{pdf_content}

NDPS Sections:
{ndps_text}

BNS Sections:
{bns_text}

BNSS Sections:
{bnss_text}

BSA Sections:
{bsa_text}

Forensic Guidelines:
{forensic_text}

Generate specific, actionable dos and donts that officers should follow during investigation, evidence handling, and convict management."""
    
    # Generate dos and donts with structured output
    @exponential_backoff_retry(max_retries=5, max_wait=60)
    def generate_dos_donts():
        return llm_model.with_structured_output(DosAndDonts).invoke(content_for_llm)
    
    dos_and_donts = generate_dos_donts()
    
    logger.info(f"Generated {len(dos_and_donts.dos)} dos and {len(dos_and_donts.donts)} donts")

    # Return updated state
    return {
        "dos": dos_and_donts.dos,
        "donts": dos_and_donts.donts,
    }