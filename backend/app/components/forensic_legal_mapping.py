from pydantic import BaseModel, Field
from app.langgraph.state import WorkflowState
from app.models.openai import llm_model
from typing import List
from app.rag.query_all import query_forensic
from app.utils.retry import exponential_backoff_retry
import logging

logger = logging.getLogger(__name__)

class ForensicGuidelines(BaseModel):
    guideline_topic: str = Field(
        description="The topic, heading, or section identifier from the forensic guide"
    )
    guideline_description: str = Field(
        description="A clear definition of what the guideline/topic covers based ONLY on the retrieved forensic text. Describe the guideline's scope, provisions, and meaning. Do NOT explain why it's relevant to the FIR - that goes in why_guideline_is_relevant."
    )
    why_guideline_is_relevant: str = Field(
        description="A clear explanation of why this forensic guideline is valid and applicable to the legal point/charge from the FIR. Explain the connection between the FIR facts and this specific guideline, making it clear why this guideline should be considered."
    )
    source: str = Field(
        description="Source information including page number, PDF document name, and source URL from the forensic guide (format: Page X, Document: [pdf_name], Source URL: [source_url])"
    )

class ForensicLegalMapping(BaseModel):
    guidelines: List[ForensicGuidelines] = Field(
        description=""
    )

class PointsToBeCharged(BaseModel):
    points_to_be_charged: List[str] = Field(
        description="List of factual points extracted directly and explicitly from the FIR text. Each point must be a direct factual statement that is explicitly stated in the FIR, with no interpretations, inferences, or additions. Maximum 10 high-quality points.",
        max_items=10
    )


def forensic_legal_mapping(state: WorkflowState) -> dict:
    """
    Map forensic investigation guidelines to FIR facts.
    """
    logger.info("Starting forensic legal mapping")
    
    if not state.get("pdf_content_in_english"):
        raise ValueError("pdf_content_in_english is required for FIR fact extraction")
    
    pdf_content = state["pdf_content_in_english"]
    logger.debug(f"FIR content length: {len(pdf_content)} characters")
    
    llm_with_structured_output = llm_model.with_structured_output(PointsToBeCharged)
    prompt = f"""
You are an expert in forensic investigation procedures for NDPS cases.

Task: Extract only factual points from the FIR text below.

Rules:
- Extract 6- 10 high-quality factual points.
- Prioritize the most legally significant and relevant facts for forensic investigation.
- Use only facts that are explicitly written in the FIR.
- Do not infer, assume, interpret, or add anything.
- Do not mention any section numbers.
- Extract only NDPS-related facts that would require forensic investigation (acts, substances, quantities, locations, actions, procedures, evidence collection).
- Each point must be a separate, clear, high-quality factual statement.
- Focus on facts that are most relevant for forensic investigation and evidence collection.
- If something is not written in the FIR, do not include it.
- Quality over quantity - select only the most important and legally significant points.

FIR Text:
{pdf_content}

Output: List only the factual points (maximum 10 high-quality points).
"""
    
    @exponential_backoff_retry(max_retries=5, max_wait=60)
    def _invoke_extract_points():
        return llm_with_structured_output.invoke(prompt)
    
    response = _invoke_extract_points()
    points = response.points_to_be_charged
    logger.info(f"Extracted {len(points)} legal points")

    guidelines_mapped = []
    for idx, point in enumerate(points, 1):
        logger.debug(f"Processing point {idx}/{len(points)}")
        results = query_forensic(point, k=5)
        logger.debug(f"Found {len(results)} relevant guidelines for point {idx}")

        # Format retrieved guidelines with chapter, headings, content, and source
        # query_forensic returns [{'chunk': {...}, 'score': float}]; chunk structure: chapter, chapter_title, headings, content, page_number, source_url, pdf_name
        guidelines_found = ""
        for i, result in enumerate(results):
            chunk = result['chunk']
            chapter = chunk.get('chapter', 'N/A')
            chapter_title = chunk.get('chapter_title', 'N/A')
            headings = chunk.get('headings', [])
            content = chunk['content']
            page_number = chunk.get('page_number')
            source_url = chunk.get('source_url')
            pdf_name = chunk.get('pdf_name', 'N/A')
            chunk_id = i + 1
            

            guidelines_found += f"Chapter: {chapter} - {chapter_title}\n"
            if headings:
                guidelines_found += f"Headings: {' > '.join(headings) if isinstance(headings, list) else headings}\n"
            guidelines_found += f"Source: Page {page_number if page_number is not None else 'N/A'}, Chunk {chunk_id}\n"
            if source_url:
                guidelines_found += f"Source URL: {source_url}\n"
            guidelines_found += f"Document: {pdf_name}\n"
            guidelines_found += f"Forensic Text:\n{content}\n"
            guidelines_found += "-" * 80 + "\n"

        # Create prompt with the legal point and retrieved guidelines
        llm_with_structured_output = llm_model.with_structured_output(ForensicLegalMapping)
        prompt = f"""
You are an expert in forensic investigation procedures for NDPS cases.

Legal Point (from FIR):
{point}

Retrieved Forensic Guide Text:
{guidelines_found}

Task:
Identify only the forensic guidelines that are directly applicable to the legal point from the FIR.

CRITICAL RULES:
1. Use ONLY the retrieved Forensic Guide text above. Do not add external knowledge, interpretations, or assumptions.
2. Each guideline must be clearly supported by the retrieved text.
3. The legal point must directly match facts that the guideline addresses according to the retrieved text.
4. You are NOT required to use all retrieved guidelines - select only what is important and relevant to the legal point.
5. If a guideline is not clearly and directly applicable based on the retrieved text, exclude it.
6. Prefer fewer accurate guidelines over many weak ones.
7. Do NOT interpret or infer connections - use only what is explicitly stated in the retrieved Forensic Guide text.

For each included guideline, return:

- guideline_topic:
  Must match the topic/heading from retrieved text (e.g. "CHAPTER 8 - NARCOTIC DRUGS AND PSYCHOTROPIC SUBSTANCES (NDPS) - Definitions According to NDPS Act (Section 2)" or "8.1 - Definitions According to NDPS Act (Section 2)").
  Format: Use chapter, chapter_title, and relevant heading from the retrieved text.

- guideline_description:
  Describe what the guideline states using ONLY the retrieved Forensic Text above.
  Do not add interpretations or external knowledge.
  Base this description solely on the exact words from the retrieved text.

- why_guideline_is_relevant:
  Explain how the legal point from the FIR relates to this guideline, based ONLY on what the retrieved Forensic Text states.
  Reference specific facts from the legal point that align with what the guideline text describes.
  Do not make assumptions or interpretations beyond what is explicitly stated.

- source:
  Format: "Page X, Document: [pdf_name], Source URL: [source_url]"
  Use the exact values from "Source:", "Document:", and "Source URL:" fields above.
  If page_number is null, use "Page N/A".
  If source_url is null, omit "Source URL:" part.
  Example: "Page 2, Document: Book A Forensic Guide for Crime Investigators" or "Page 2, Document: Book A Forensic Guide for Crime Investigators, Source URL: https://..."

If no guideline from the retrieved text directly applies to the legal point, return an empty list [].
Return output as JSON list only.
"""
        
        @exponential_backoff_retry(max_retries=5, max_wait=60)
        def _invoke_map_guidelines():
            return llm_with_structured_output.invoke(prompt)
        
        response = _invoke_map_guidelines()
        guidelines_mapped.append(response.guidelines)
        logger.debug(f"Mapped point {idx} to {len(response.guidelines)} guidelines")

    # Flatten the list of lists into a single list
    flattened_guidelines = []
    for chunk_guidelines in guidelines_mapped:
        flattened_guidelines.extend(chunk_guidelines)
    
    # Convert back to list of dicts
    final_guidelines = [guideline.model_dump() if hasattr(guideline, 'model_dump') else guideline for guideline in flattened_guidelines]
    
    logger.info(f"Mapped {len(final_guidelines)} forensic guidelines")
    print("🍺")
    print(final_guidelines)
    return {
        "forensic_guidelines_mapped": final_guidelines
    }
