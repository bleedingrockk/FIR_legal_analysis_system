from pydantic import BaseModel, Field
from app.langgraph.state import WorkflowState
from app.models.openai import llm_model
from typing import List
from app.rag.query_all import query_forensic
import time
import random
from functools import wraps

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


def _merge_duplicate_guidelines(guideline_topic: str, duplicate_guidelines: List[ForensicGuidelines]) -> ForensicGuidelines:
    """
    Merge duplicate guidelines using LLM to combine information from all duplicates.
    
    Args:
        guideline_topic: The guideline topic that has duplicates
        duplicate_guidelines: List of ForensicGuidelines objects with the same guideline_topic
        
    Returns:
        Merged ForensicGuidelines object
    """
    # Format duplicates for LLM
    duplicates_text = ""
    for idx, guideline in enumerate(duplicate_guidelines, 1):
        duplicates_text += f"\n--- Duplicate {idx} ---\n"
        duplicates_text += f"Guideline Description: {guideline.guideline_description}\n"
        duplicates_text += f"Why Guideline is Relevant: {guideline.why_guideline_is_relevant}\n"
        duplicates_text += f"Source: {guideline.source}\n"
    
    llm_with_structured_output = llm_model.with_structured_output(ForensicGuidelines)
    prompt = f"""
You are an expert in forensic investigation procedures for NDPS cases. You need to merge duplicate entries for the same guideline topic.

Guideline Topic: {guideline_topic}

Duplicate Entries:
{duplicates_text}

Task:
Merge these duplicate entries into a single, comprehensive entry that:
1. Combines the best information from all duplicates
2. Creates a clear, comprehensive guideline_description using information from all duplicates
3. Creates a comprehensive why_guideline_is_relevant that combines all relevant points
4. Uses the most appropriate source (or combines sources if needed)

Rules:
- Use the guideline_topic exactly: {guideline_topic}
- Combine information from all duplicates - do not lose important details
- Ensure the merged entry is more comprehensive than any single duplicate
- For source, use the format: "Page X, Document: [pdf_name], Source URL: [source_url]" from the most relevant duplicate, or combine if they differ
- Maintain accuracy - only use information that is present in the duplicates

Return the merged guideline.
"""
    
    @exponential_backoff_retry(max_retries=5, max_wait=60)
    def _invoke_merge():
        return llm_with_structured_output.invoke(prompt)
    
    merged = _invoke_merge()
    print(f"    ✅ Merged {guideline_topic}")
    return merged

def forensic_legal_mapping(state: WorkflowState) -> dict:
    """
    Map forensic investigation guidelines to FIR facts.
    """
    print("\n" + "=" * 80)
    print("🔍 [forensic_legal_mapping] Starting forensic guideline mapping...")
    print("=" * 80)
    
    if not state.get("pdf_content_in_english"):
        raise ValueError("pdf_content_in_english is required for FIR fact extraction")
    
    pdf_content = state["pdf_content_in_english"]
    print(f"📝 [forensic_legal_mapping] FIR content length: {len(pdf_content)} characters")
    print(f"📝 [forensic_legal_mapping] FIR preview: {pdf_content[:200]}...")

    # Step 1: Extract actionable legal points from FIR content
    print("\n[forensic_legal_mapping] Step 1: Extracting legal points from FIR content...")
    llm_with_structured_output = llm_model.with_structured_output(PointsToBeCharged)
    prompt = f"""
You are an expert in forensic investigation procedures for NDPS cases.

Task: Extract only factual points from the FIR text below.

Rules:
- Extract MAXIMUM 10 high-quality factual points.
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

    print("[forensic_legal_mapping] Calling LLM to extract legal points...")
    
    @exponential_backoff_retry(max_retries=5, max_wait=60)
    def _invoke_extract_points():
        return llm_with_structured_output.invoke(prompt)
    
    response = _invoke_extract_points()
    
    points = response.points_to_be_charged
    print(f"✅ [forensic_legal_mapping] Extracted {len(points)} legal points:")
    for i, point in enumerate(points, 1):
        print(f"   {i}. {point[:100]}...")

    guidelines_mapped = []
    print(f"\n[forensic_legal_mapping] Step 2: Mapping {len(points)} points to forensic guidelines...")
    for idx, point in enumerate(points, 1):
        print(f"\n[{idx}/{len(points)}] Processing point: {point[:80]}...")
        
        # Retrieve relevant forensic guidelines using query_forensic
        print(f"  🔎 [{idx}/{len(points)}] Searching FAISS index...")
        results = query_forensic(point, k=5)
        print(f"  ✅ [{idx}/{len(points)}] Found {len(results)} relevant guidelines")

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
            
            # Build topic identifier from chapter and headings
            topic_parts = []
            if chapter:
                topic_parts.append(chapter)
            if chapter_title:
                topic_parts.append(chapter_title)
            if headings:
                # Use the most relevant heading (usually the last one)
                topic_parts.append(headings[-1] if isinstance(headings, list) else str(headings))
            
            topic = " - ".join([p for p in topic_parts if p and p != 'N/A'])
            
            guidelines_found += f"{topic}\n"
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
        print(f"  🤖 [{idx}/{len(points)}] Calling LLM to map point to guidelines...")
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
        print(f"  ✅ [{idx}/{len(points)}] Mapped to {len(response.guidelines)} guidelines")

    # Flatten the list of lists into a single list
    print("\n[forensic_legal_mapping] Step 3: Flattening and deduplicating results...")
    flattened_guidelines = []
    for chunk_guidelines in guidelines_mapped:
        flattened_guidelines.extend(chunk_guidelines)
    
    # Group guidelines by guideline_topic to identify duplicates
    guidelines_by_topic = {}
    for guideline in flattened_guidelines:
        guideline_topic = guideline.guideline_topic
        if guideline_topic not in guidelines_by_topic:
            guidelines_by_topic[guideline_topic] = []
        guidelines_by_topic[guideline_topic].append(guideline)
    
    # Merge duplicates using LLM if they exist
    deduplicated_guidelines = []
    for guideline_topic, duplicate_guidelines in guidelines_by_topic.items():
        if len(duplicate_guidelines) == 1:
            # No duplicates, just add the guideline
            deduplicated_guidelines.append(duplicate_guidelines[0])
        else:
            # Duplicates found - merge them using LLM
            print(f"  🔄 Merging {len(duplicate_guidelines)} duplicates for {guideline_topic}...")
            merged_guideline = _merge_duplicate_guidelines(guideline_topic, duplicate_guidelines)
            deduplicated_guidelines.append(merged_guideline)
    
    # Convert back to list of dicts
    final_guidelines = [guideline.model_dump() if hasattr(guideline, 'model_dump') else guideline for guideline in deduplicated_guidelines]
    
    print(f"✅ [forensic_legal_mapping] Total guidelines before deduplication: {len(flattened_guidelines)}")
    print(f"✅ [forensic_legal_mapping] Total guidelines after deduplication: {len(final_guidelines)}")
    print("=" * 80)
    
    return {
        "forensic_guidelines_mapped": final_guidelines
    }
