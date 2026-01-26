"""
Utility functions for route handlers.
"""

import json
from typing import List, Dict, Any


def parse_sections(sections_data) -> List[Dict[str, Any]]:
    """
    Parse sections data - handle both string and list formats.
    
    Args:
        sections_data: Sections data in string or list format
        
    Returns:
        List of section dictionaries
    """
    if not sections_data:
        return []
    if isinstance(sections_data, str):
        try:
            # Replace single quotes with double quotes for JSON parsing
            return json.loads(sections_data.replace("'", '"'))
        except (json.JSONDecodeError, ValueError):
            return []
    return sections_data if isinstance(sections_data, list) else []


def format_state_for_display(state: dict) -> dict:
    """Format the workflow state for display in templates (no file paths)."""
    ndps_sections = parse_sections(state.get("sections_mapped"))
    bns_sections = parse_sections(state.get("bns_sections_mapped"))
    bnss_sections = parse_sections(state.get("bnss_sections_mapped"))
    bsa_sections = parse_sections(state.get("bsa_sections_mapped"))
    forensic_guidelines = parse_sections(state.get("forensic_guidelines_mapped"))
    next_steps = state.get("next_steps") or []
    investigation_plan = state.get("investigation_plan") or []
    evidence_checklist = state.get("evidence_checklist")

    formatted = {
        "workflow_id": state.get("workflow_id"),
        "pdf_filename": state.get("pdf_filename") or state.get("pdf_path"),
        "pdf_content_preview": (
            (state.get("pdf_content") or "")[:500] + "..."
            if state.get("pdf_content") else None
        ),
        "pdf_content_in_english_preview": (
            (state.get("pdf_content_in_english") or "")[:500] + "..."
            if state.get("pdf_content_in_english") else None
        ),
        "fir_facts": state.get("fir_facts"),
        "ndps_sections": ndps_sections,
        "bns_sections": bns_sections,
        "bnss_sections": bnss_sections,
        "bsa_sections": bsa_sections,
        "forensic_guidelines": forensic_guidelines,
        "next_steps": next_steps,
        "investigation_plan": investigation_plan,
        "evidence_checklist": evidence_checklist,
        "stats": {
            "ndps_count": len(ndps_sections),
            "bns_count": len(bns_sections),
            "bnss_count": len(bnss_sections),
            "bsa_count": len(bsa_sections),
            "forensic_count": len(forensic_guidelines),
            "next_steps_count": len(next_steps) + len(investigation_plan),
        },
    }
    return formatted
