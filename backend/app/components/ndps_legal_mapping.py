from pydantic import BaseModel, Field
from app.langgraph.state import WorkflowState
from app.models.openai import llm_model
from typing import List
from app.rag.query_all import query_ndps
import time
import random
from functools import wraps

class SectionsCharged(BaseModel):
    section_number: str = Field(
        description="The section number of the legal provision"
    )
    section_description: str = Field(
        description="A clear definition of what the section covers based ONLY on the retrieved legal text. Describe the section's scope, provisions, and legal meaning. Do NOT explain why it's relevant to the FIR - that goes in why_section_is_relevant."
    )
    why_section_is_relevant: str = Field(
        description="A clear explanation of why this section is valid and applicable to the legal point/charge from the FIR. Explain the connection between the FIR facts and this specific section, making it clear why this section should be charged."
    )
    source: str = Field(
        description="Source information including page number, PDF document name, and source URL from the NDPS Act document (format: Page X, Document: [pdf_name], Source URL: [source_url])"
    )

class NdpsLegalMapping(BaseModel):
    sections: List[SectionsCharged] = Field(
        description=""
    )

class PointsToBeCharged(BaseModel):
    points_to_be_charged: List[str] = Field(
        description="List of factual points extracted directly and explicitly from the FIR text. Each point must be a direct factual statement that is explicitly stated in the FIR, with no interpretations, inferences, or additions. Maximum 10 high-quality points.",
        max_items=10
    )


def exponential_backoff_retry(max_retries=5, max_wait=60):
    """
    Decorator for exponential backoff retry on LLM calls.
    
    Args:
        max_retries: Maximum number of retry attempts (5 means 1 initial + 5 retries = 6 total)
        max_wait: Maximum wait time in seconds (60 seconds = 1 minute)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            base_wait = 1  # Start with 1 second
            
            while attempt <= max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt >= max_retries:
                        print(f"❌ Failed after {max_retries + 1} attempts: {str(e)}")
                        raise
                    
                    # Calculate wait time: exponential backoff with jitter, capped at max_wait
                    wait_time = min(base_wait * (2 ** attempt), max_wait)
                    # Add jitter (random 0-10% to avoid thundering herd)
                    wait_time = wait_time * (1 + random.uniform(0, 0.1))
                    
                    attempt += 1
                    print(f"⚠️  LLM call failed (attempt {attempt}/{max_retries + 1}), retrying in {wait_time:.1f}s...")
                    time.sleep(wait_time)
            
            # Should never reach here, but just in case
            raise Exception(f"Failed after {max_retries + 1} attempts")
        
        return wrapper
    return decorator


def _merge_duplicate_sections(section_number: str, duplicate_sections: List[SectionsCharged]) -> SectionsCharged:
    """
    Merge duplicate sections using LLM to combine information from all duplicates.
    
    Args:
        section_number: The section number that has duplicates
        duplicate_sections: List of SectionsCharged objects with the same section_number
        
    Returns:
        Merged SectionsCharged object
    """
    # Format duplicates for LLM
    duplicates_text = ""
    for idx, section in enumerate(duplicate_sections, 1):
        duplicates_text += f"\n--- Duplicate {idx} ---\n"
        duplicates_text += f"Section Description: {section.section_description}\n"
        duplicates_text += f"Why Section is Relevant: {section.why_section_is_relevant}\n"
        duplicates_text += f"Source: {section.source}\n"
    
    llm_with_structured_output = llm_model.with_structured_output(SectionsCharged)
    prompt = f"""
You are an expert in NDPS law. You need to merge duplicate entries for the same section number.

Section Number: {section_number}

Duplicate Entries:
{duplicates_text}

Task:
Merge these duplicate entries into a single, comprehensive entry that:
1. Combines the best information from all duplicates
2. Creates a clear, comprehensive section_description using information from all duplicates
3. Creates a comprehensive why_section_is_relevant that combines all relevant points
4. Uses the most appropriate source (or combines sources if needed)

Rules:
- Use the section_number exactly: {section_number}
- Combine information from all duplicates - do not lose important details
- Ensure the merged entry is more comprehensive than any single duplicate
- For source, use the format: "Page X, Document: [pdf_name], Source URL: [source_url]" from the most relevant duplicate, or combine if they differ
- Maintain accuracy - only use information that is present in the duplicates

Return the merged section.
"""
    
    @exponential_backoff_retry(max_retries=5, max_wait=60)
    def _invoke_merge():
        return llm_with_structured_output.invoke(prompt)
    
    merged = _invoke_merge()
    print(f"    ✅ Merged {section_number}")
    return merged

def ndps_legal_mapping(state: WorkflowState) -> dict:
    """
    Map NDPS legal provisions to FIR facts.
    """
    print("\n" + "=" * 80)
    print("🔍 [ndps_legal_mapping] Starting legal mapping...")
    print("=" * 80)
    
    if not state.get("pdf_content_in_english"):
        raise ValueError("pdf_content_in_english is required for FIR fact extraction")
    
    pdf_content = state["pdf_content_in_english"]
    print(f"📝 [ndps_legal_mapping] FIR content length: {len(pdf_content)} characters")
    print(f"📝 [ndps_legal_mapping] FIR preview: {pdf_content[:200]}...")

    # Step 1: Extract actionable legal points from FIR content
    print("\n[ndps_legal_mapping] Step 1: Extracting legal points from FIR content...")
    llm_with_structured_output = llm_model.with_structured_output(PointsToBeCharged)
    prompt = f"""
You are an expert in Indian NDPS law.

Task: Extract only factual points from the FIR text below.

Rules:
- Extract MAXIMUM 10 high-quality factual points.
- Prioritize the most legally significant and relevant facts.
- Use only facts that are explicitly written in the FIR.
- Do not infer, assume, interpret, or add anything.
- Do not mention any section numbers.
- Extract only NDPS-related facts (acts, substances, quantities, locations, actions, procedures).
- Each point must be a separate, clear, high-quality factual statement.
- Focus on facts that are most relevant for legal charging and prosecution.
- If something is not written in the FIR, do not include it.
- Quality over quantity - select only the most important and legally significant points.

FIR Text:
{pdf_content}

Output: List only the factual points (maximum 10 high-quality points).
"""

    print("[ndps_legal_mapping] Calling LLM to extract legal points...")
    
    @exponential_backoff_retry(max_retries=5, max_wait=60)
    def _invoke_extract_points():
        return llm_with_structured_output.invoke(prompt)
    
    response = _invoke_extract_points()
    
    points = response.points_to_be_charged
    print(f"✅ [ndps_legal_mapping] Extracted {len(points)} legal points:")
    for i, point in enumerate(points, 1):
        print(f"   {i}. {point[:100]}...")

    sections_mapped = []
    print(f"\n[ndps_legal_mapping] Step 2: Mapping {len(points)} points to NDPS sections...")
    for idx, point in enumerate(points, 1):
        print(f"\n[{idx}/{len(points)}] Processing point: {point[:80]}...")
        
        # Retrieve relevant NDPS Act sections using query_ndps
        print(f"  🔎 [{idx}/{len(points)}] Searching FAISS index...")
        results = query_ndps(point, k=5)
        print(f"  ✅ [{idx}/{len(points)}] Found {len(results)} relevant sections")

        # Format retrieved sections with section heading, exact legal wording, and source
        # query_ndps returns [{'chunk': {...}, 'score': float}]; chunk structure: section, subsection (may be null), chapter, chapter_heading, content, page_number, source_url, pdf_name
        sections_found = ""
        for i, result in enumerate(results):
            chunk = result['chunk']
            section = chunk['section']
            subsection = chunk.get('subsection')  # May be null
            chapter = chunk['chapter']
            chapter_heading = chunk['chapter_heading']
            content = chunk['content']
            page_number = chunk['page_number']
            source_url = chunk['source_url']
            pdf_name = chunk['pdf_name']
            chunk_id = i + 1
            
            # Build section number (section + subsection if present)
            section_num = section + (f' {subsection}' if subsection else '')
            
            sections_found += f"{section_num}\n"
            sections_found += f"Chapter: {chapter} - {chapter_heading}\n"
            sections_found += f"Source: Page {page_number}, Chunk {chunk_id}\n"
            sections_found += f"Source URL: {source_url}\n"
            sections_found += f"Document: {pdf_name}\n"
            sections_found += f"Legal Text:\n{content}\n"
            sections_found += "-" * 80 + "\n"

        # Create prompt with the legal point and retrieved sections
        print(f"  🤖 [{idx}/{len(points)}] Calling LLM to map point to sections...")
        llm_with_structured_output = llm_model.with_structured_output(NdpsLegalMapping)
        prompt = f"""
You are an expert in NDPS law.

Legal Point (from FIR):
{point}

Retrieved NDPS Act Text:
{sections_found}

Task:
Identify only the NDPS sections that are directly applicable to the legal point from the FIR.

CRITICAL RULES:
1. Use ONLY the retrieved NDPS Act text above. Do not add external knowledge, legal interpretations, or assumptions.
2. Each section must be clearly supported by the retrieved text.
3. The legal point must directly match facts that the section addresses according to the retrieved text.
4. You are NOT required to use all retrieved sections - select only what is important and relevant to the legal point.
5. If a section is not clearly and directly applicable based on the retrieved text, exclude it.
6. Prefer fewer accurate sections over many weak ones.
7. Do NOT interpret or infer connections - use only what is explicitly stated in the retrieved NDPS Act text.

For each included section, return:

- section_number:
  Must match exactly as shown in retrieved text (e.g. "Section 1 (1)", "Section 20", including sub-clauses like 20(b-ii)(B), 29(1), etc.)
  Format: Include subsection if shown (e.g. "Section 20 (1)" or "Section 20").

- section_description:
  Describe what the section states using ONLY the retrieved Legal Text above.
  Do not add interpretations or external knowledge.
  Base this description solely on the exact words from the retrieved text.

- why_section_is_relevant:
  Explain how the legal point from the FIR relates to this section, based ONLY on what the retrieved Legal Text states.
  Reference specific facts from the legal point that align with what the section text describes.
  Do not make assumptions or interpretations beyond what is explicitly stated.

- source:
  Format: "Page X, Document: [pdf_name], Source URL: [source_url]"
  Use the exact values from "Source:", "Document:", and "Source URL:" fields above.
  Example: "Page 15, Document: narcotic_drugs_and_psychotropic_substances_act_1985.pdf, Source URL: https://www.indiacode.nic.in/..."

If no section from the retrieved text directly applies to the legal point, return an empty list [].
Return output as JSON list only.
"""
        
        @exponential_backoff_retry(max_retries=5, max_wait=60)
        def _invoke_map_sections():
            return llm_with_structured_output.invoke(prompt)
        
        response = _invoke_map_sections()
        sections_mapped.append(response.sections)
        print(f"  ✅ [{idx}/{len(points)}] Mapped to {len(response.sections)} sections")

    # Flatten the list of lists into a single list
    print("\n[ndps_legal_mapping] Step 3: Flattening and deduplicating results...")
    flattened_sections = []
    for chunk_sections in sections_mapped:
        flattened_sections.extend(chunk_sections)
    
    # Group sections by section_number to identify duplicates
    sections_by_number = {}
    for section in flattened_sections:
        section_number = section.section_number
        if section_number not in sections_by_number:
            sections_by_number[section_number] = []
        sections_by_number[section_number].append(section)
    
    # Merge duplicates using LLM if they exist
    deduplicated_sections = []
    for section_number, duplicate_sections in sections_by_number.items():
        if len(duplicate_sections) == 1:
            # No duplicates, just add the section
            deduplicated_sections.append(duplicate_sections[0])
        else:
            # Duplicates found - merge them using LLM
            print(f"  🔄 Merging {len(duplicate_sections)} duplicates for {section_number}...")
            merged_section = _merge_duplicate_sections(section_number, duplicate_sections)
            deduplicated_sections.append(merged_section)
    
    # Convert back to list of dicts
    final_sections = [section.model_dump() if hasattr(section, 'model_dump') else section for section in deduplicated_sections]
    
    print(f"✅ [ndps_legal_mapping] Total sections before deduplication: {len(flattened_sections)}")
    print(f"✅ [ndps_legal_mapping] Total sections after deduplication: {len(final_sections)}")
    print("=" * 80)
    
    return {
        "sections_mapped": final_sections
    }