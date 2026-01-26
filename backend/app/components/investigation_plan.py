from typing import List, Optional
from pydantic import BaseModel
from app.langgraph.state import WorkflowState
from app.models.openai import llm_model
from app.utils.retry import exponential_backoff_retry
import logging

logger = logging.getLogger(__name__)

class PlanPoint(BaseModel):
    title: str                 # e.g. "Immediate Action"
    date_range: Optional[str]  # e.g. "19/09/2025" or "19–20 Sep"
    description: str           # Full paragraph of actions

class InvestigationPlan(BaseModel):
    points: List[PlanPoint]

PROMPT = """
You are a senior Indian criminal law expert and investigation officer.

Analyse the FIR text below and generate a professional, chronological, court-ready Step-wise Investigation Plan for the case.

The plan must be realistic, procedural, and compliant with:
- NDPS Act
- CrPC
- Juvenile Justice Act (if minor involved)

Do NOT ask questions.
Do NOT request extra information.
Work only with the FIR content and generate a legally sound investigation roadmap.

If any fact is missing from FIR, write the step as "to be verified" or "to be completed".

The output must always follow this structure:

1. Immediate Actions (Day 0–1)
   - FIR compliance steps
   - Production before Magistrate/JJB
   - NDPS reporting (Sections 52, 52A, 57)
   - CWC / juvenile safeguards if minor
   - Preservation of evidence

2. Child Welfare & Juvenile Safeguards (only if accused appears minor)
   - JJB production within 24 hours
   - Guardian intimation
   - Age verification process
   - CWC involvement

3. Documentation & Procedural Compliance
   - Panchnama
   - Section 52A inventory
   - Seal and chain of custody
   - Case diary entries

4. Forensic & Sampling Process
   - Magistrate-supervised sampling
   - Dispatch to FSL
   - Acknowledgement and report tracking

5. Witness Examination
   - Police witnesses
   - Panch witnesses
   - Independent witnesses
   - Special witnesses (dog handler, FSL officer etc.)

6. Evidence Development
   - CCTV collection
   - Digital evidence (mobile, CDR, extraction)
   - Travel records / location evidence
   - Identification of co-accused or supplier

7. NDPS Legal Compliance Review
   - Section 42/43/50 compliance
   - Documentation of rights explained
   - Proper reporting to superior officers

8. Bail & Custody Considerations
   - NDPS bail limitations
   - Juvenile Justice bail principles (if applicable)
   - Custody status and court approach

9. Charge-sheet Preparation
   - Evidence compilation
   - Expert reports
   - Section 173 CrPC filing timeline
   - Final legal scrutiny

10. Timeline Summary
    - Day-wise or week-wise investigation progression
    - Pending steps clearly marked

Style requirements:
- Use formal Indian legal English
- Use clear, professional headings
- Avoid theory, focus on actionable investigation steps
- Do not hallucinate facts; use conditional phrasing where FIR is silent

FIR Text:
[PASTE FIR HERE]
"""

def investigation_plan(state: WorkflowState) -> dict:
    """
    Generate investigation plan based on FIR facts.
    """
    logger.info("Starting investigation plan generation")
    
    if not state.get("pdf_content_in_english"):
        raise ValueError("pdf_content_in_english is required for FIR fact extraction")
    
    pdf_content = state["pdf_content_in_english"]
    logger.debug(f"FIR content length: {len(pdf_content)} characters")

    llm_with_structured_output = llm_model.with_structured_output(InvestigationPlan)
    prompt = PROMPT.replace("[PASTE FIR HERE]", pdf_content)
    
    @exponential_backoff_retry(max_retries=5, max_wait=60)
    def _invoke_investigation_plan():
        return llm_with_structured_output.invoke(prompt)
    
    response = _invoke_investigation_plan()
    state["investigation_plan"] = response.points
    logger.info(f"Generated investigation plan with {len(response.points)} points")
    return {
        "investigation_plan": response.points
    }
    