import os
from google.cloud.translate_v3.services.translation_service import TranslationServiceClient
from app.langgraph.state import WorkflowState

# Set credentials for Google Cloud Translate
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"app/translator/secret/ndps-rag-3da784f44836.json"

# Project ID for Google Cloud Translate
PROJECT_ID = "ndps-rag"

def translate_to_english(state: WorkflowState) -> dict:
    """
    Translate PDF content to English using Google Cloud Translate.
    Works as a LangGraph node that accepts state and returns updated state.
    
    Args:
        state: WorkflowState containing pdf_content
        
    Returns:
        Dictionary with translated content in pdf_content_in_english
        
    Raises:
        ValueError: If pdf_content is missing
        Exception: If translation fails
    """
       
    if not state.get("pdf_content"):
        raise ValueError("pdf_content is required for translation")
    
    pdf_content = state["pdf_content"]

    try:
        # Initialize the v3 Client
        client = TranslationServiceClient()
        
        # Setup location and parent path
        location = "global"
        parent = f"projects/{PROJECT_ID}/locations/{location}"

        # Request translation
        response = client.translate_text(
            request={
                "parent": parent,
                "contents": [pdf_content],
                "mime_type": "text/plain",
                "target_language_code": "en",  # Translating TO English
            }
        )

        # Extract translated text
        translated_text = ""
        for translation in response.translations:
            translated_text = translation.translated_text
            break  # Get first translation result
        
        print(f"✅ [translate_to_english] Translation completed, output length: {len(translated_text)} characters")
        print("=" * 80)
        
        # Return updated state with translated content
        return {"pdf_content_in_english": translated_text}
    
    except Exception as e:
        raise Exception(f"Error translating content: {str(e)}")