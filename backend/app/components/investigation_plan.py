from pydantic import BaseModel, Field
from app.langgraph.state import WorkflowState
from app.models.openai import llm_model
from typing import List
from app.rag.query_all import query_forensic
import time
import random
from functools import wraps


# ------------------ Schemas ------------------

class NextSteps(BaseModel):
    next_steps: List[str] = Field(
        description="List of grounded next steps based strictly on retrieved legal content"
    )

class Summary_Points(BaseModel):
    summary_points: List[str] = Field(
        description="5-6 factual points from FIR that affect investigation/procedure"
    )


# ------------------ Retry Decorator ------------------

def exponential_backoff_retry(max_retries=5, max_wait=60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            base_wait = 1

            while attempt <= max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt >= max_retries:
                        raise

                    wait_time = min(base_wait * (2 ** attempt), max_wait)
                    wait_time *= (1 + random.uniform(0, 0.1))

                    print(f"⚠️ Retry {attempt+1}/{max_retries+1} in {wait_time:.1f}s")
                    time.sleep(wait_time)
                    attempt += 1

        return wrapper
    return decorator


# ------------------ Main Logic ------------------

def investigation_plan(state: WorkflowState) -> dict:

    if not state.get("pdf_content_in_english"):
        raise ValueError("pdf_content_in_english is required")

    pdf_content = state["pdf_content_in_english"]

    print("🔍 Extracting FIR facts...")

    llm_structured = llm_model.with_structured_output(Summary_Points)

    fir_prompt = f"""
You are extracting structured facts from an FIR for NDPS investigation.

Rules:
- Extract only facts explicitly stated.
- Do NOT infer, assume, or add.
- Each point must affect legal procedure.
- Keep to 5–6 points only.

Examples:
- "Accused found in possession of 10 kg ganja"
- "Seizure occurred at railway station"
- "Samples were not drawn at spot"
- "Accused is juvenile"

FIR Text:
{pdf_content}

Return only 5–6 factual points.
"""

    @exponential_backoff_retry()
    def extract_facts():
        return llm_structured.invoke(fir_prompt)

    response = extract_facts()
    points = response.summary_points

    print(f"✅ Extracted {len(points)} FIR points")

    # ------------------ RAG Retrieval ------------------

    try:
        all_results = []
        for p in points:
            all_results.extend(query_forensic(p, k=5))
    except FileNotFoundError as e:
        print(f"⚠️ Forensic index not found: {e}")
        print("⚠️ Skipping forensic RAG retrieval, generating steps without forensic context")
        all_results = []

    # Deduplicate similar chunks
    seen = set()
    unique_chunks = []
    for r in all_results:
        text = r["chunk"]["content"]
        if text not in seen:
            seen.add(text)
            unique_chunks.append(text)

    rag_context = "\n\n".join(f"- {c}" for c in unique_chunks) if unique_chunks else "No specific procedural guidance available from forensic guide."

    print(f"📚 Retrieved {len(unique_chunks)} grounded legal chunks")

    # ------------------ Generate Next Steps ------------------

    llm_structured = llm_model.with_structured_output(NextSteps)

    steps_prompt = f"""
You are generating an NDPS investigation plan.

IMPORTANT RULES:
- Use ONLY the information provided below.
- Do NOT use outside knowledge.
- Do NOT invent steps.
- Each step must be clearly supported by the content.

Legal / Procedural Information:
{rag_context}

Task:
Convert this into a concise step-by-step list of actions for the Investigating Officer.

Output rules:
- Each step must be short and actionable
- Max 8 steps
- If no procedural guidance is available, generate general investigation steps based on standard NDPS procedures
"""

    @exponential_backoff_retry()
    def generate_steps():
        return llm_structured.invoke(steps_prompt)

    response = generate_steps()
    next_steps = response.next_steps

    print(f"✅ Generated {len(next_steps)} grounded next steps")

    return {
        "next_steps": next_steps
    }
