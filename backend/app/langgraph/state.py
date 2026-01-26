from langgraph.graph import MessagesState
from typing import List, Any

class WorkflowState(MessagesState):
    pdf_path: str | None = None
    pdf_bytes: bytes | None = None
    pdf_filename: str | None = None
    pdf_content: str | None = None
    pdf_content_in_english: str | None = None
    fir_facts: dict | None = None
    sections_mapped: List[dict] | None = None
    bns_sections_mapped: List[dict] | None = None
    bnss_sections_mapped: List[dict] | None = None
    bsa_sections_mapped: List[dict] | None = None
    forensic_guidelines_mapped: List[dict] | None = None
    investigation_plan: List[dict] | None = None
    next_steps: List[str] | None = None
    evidence_checklist: str | List[str] | None = None