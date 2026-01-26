import os
import requests
import uuid
import json
from app.langgraph.state import WorkflowState

DEMO_TEXT = """
Date: 19/09/2025

My name is Dineshji Parthaji Solanki, ASI Buckle No. 946, posted at Bharuch Railway Police Station, presently working in NDPS Dedicated Team, GRP Vadodara Camp – Surat.

I state in person that, as per instructions of In-charge Director General of Police (Railways) Shri Parikshita Rathod and Superintendent of Police Shri Abhay Solanki, special instructions were given to prevent illegal transportation of narcotic drugs into Gujarat through railway trains. Accordingly, under the guidance of PSI Shri D.D. Vankar, SOG Western Railway, Vadodara, we along with NDPS Dedicated Team and other police staff were present on duty at Surat Railway Station on 19/09/2025.

At around 10:25 hours, near the Speed Parcel Office gate on Platform No. 1, we noticed one person behaving suspiciously. He was carrying:

One grey-black backpack (five chains) with “Skybags” written on it

One maroon handbag with red strip

On enquiry, he became nervous. RPF dog squad was called. The dog named Casper indicated suspicion on both bags.

On further questioning, the person admitted that both bags contained ganja (cannabis). He disclosed his name as:
Anuj S/o Chintamani, caste Yadav, age 16 years, occupation labour in embroidery, residing at Sureshbhai’s hut near Bumba Gate, Amroli Awas, Surat. Permanent address: Village Mungra Badshahpur, District Jaunpur, Uttar Pradesh. Mobile No. 9984168824.

He stated he had no pass, permit or legal authority to possess the narcotic substance.

Panch witnesses were called. Legal procedure under NDPS Act was explained to the accused in Hindi. He consented for search to be conducted by police officers.

Personal search recovered:

One Motorola keypad mobile phone (value ₹200)

₹300 cash

One railway ticket dated 18/09/2025 from Vijayawada to Valsad

Search of bags revealed:

From backpack: 4 bundles wrapped in brown tape

From handbag: 1 bundle wrapped in brown tape

FSL officer Shri J.K. Sisodia arrived at the spot. Preliminary testing using Narcotics Testing Kit confirmed the substance as cannabis (ganja).

Weights recorded:

From backpack: Net ganja weight 10.075 kg

From handbag: Net ganja weight 3.025 kg

Total ganja seized: 13.100 kg

Market value assessed:

₹10,000 per kg

Total value: ₹1,31,000

All seized material was sealed properly:

Backpack ganja sealed as Muddamal-A

Handbag ganja sealed as Muddamal-B

Bags and packing material sealed as Muddamal-C

All procedures were done in presence of:

Panch witnesses

Police officers

FSL officer

Child Welfare Officer

Videography and photography conducted

Accused stated that he received these bundles from an unknown person near Vijayawada forest area for ₹40,000 and was instructed to deliver them near Katargam GIDC, Surat.

The entire procedure, seizure memo, notices, and documents were explained to the accused in Hindi. He understood and signed.

Therefore, the accused Anuj S/o Chintamani Yadav has committed offence under Sections 8(c), 20(b)(ii)(B), 29 of the NDPS Act, for illegal possession and transportation of ganja for financial gain.

Complaint typed as per my statement, read over to me, found correct and signed.

Signed
(H.D. Vyas)
Police Inspector
Surat Railway Police Station
"""

def translate_to_english(state: WorkflowState) -> dict:
    """
    Translate PDF content to English using Azure Translator.
    Works as a LangGraph node that accepts state and returns updated state.
    
    Args:
        state: WorkflowState containing pdf_content
        
    Returns:
        Dictionary with translated content in pdf_content_in_english
    """
    if not state.get("pdf_content"):
        raise ValueError("pdf_content is required for translation")
    
    # pdf_content = state["pdf_content"]
    # print("Translation started")
    # try:
    #     # Retrieve configuration from environment variables
    #     key = os.environ.get("AZURE_TRANSLATOR_KEY")
    #     location = os.environ.get("AZURE_TRANSLATOR_LOCATION")
    #     endpoint = os.environ.get("AZURE_TRANSLATOR_ENDPOINT", "https://api.cognitive.microsofttranslator.com")
        
    #     if not key or not location:
    #         raise ValueError("AZURE_TRANSLATOR_KEY and AZURE_TRANSLATOR_LOCATION must be set in .env")

    #     path = '/translate'
    #     constructed_url = endpoint + path

    #     params = {
    #         'api-version': '3.0',
    #         'to': ['en']  # Translating TO English
    #     }

    #     headers = {
    #         'Ocp-Apim-Subscription-Key': key,
    #         # location required if you're using a multi-service or regional (not global) resource.
    #         'Ocp-Apim-Subscription-Region': location,
    #         'Content-type': 'application/json',
    #         'X-ClientTraceId': str(uuid.uuid4())
    #     }

    #     # You can pass more than one object in body.
    #     body = [{
    #         'text': pdf_content
    #     }]

    #     print(f"📡 [translate_to_english] Sending request to {endpoint} (timeout=10s)...")
    #     request = requests.post(constructed_url, params=params, headers=headers, json=body, timeout=10)
    #     print("✅ [translate_to_english] Received response from Azure.")
        
    #     response = request.json()

    #     # Check for error in response
    #     if isinstance(response, dict) and "error" in response:
    #          raise Exception(f"Azure API Error: {response['error']}")

    #     # Extract translated text
    #     # Response structure is valid for multiple inputs: [{'translations': [{'text': '...', 'to': 'en'}]}]
    #     translated_text = response[0]['translations'][0]['text']
        
    #     print(f"✅ [translate_to_english] Translation completed, output length: {len(translated_text)} characters")
    #     print("=" * 80)
        
    #     return {"pdf_content_in_english": translated_text}

    # except Exception as e:
    #     raise Exception(f"Error translating content: {str(e)}")

    #==================================================================
    global DEMO_TEXT
    return {"pdf_content_in_english": DEMO_TEXT}


if __name__ == "__main__":
    # For local testing - Direct API Call (No project imports needed)
    from dotenv import load_dotenv
    import os
    import requests
    import uuid
    import json
    
    # Load env from .env in current or parent directory
    load_dotenv(".env")
    
    print("🚀 Starting Translator Direct Test...")

    key = os.environ.get("AZURE_TRANSLATOR_KEY")
    location = os.environ.get("AZURE_TRANSLATOR_LOCATION")
    endpoint = os.environ.get("AZURE_TRANSLATOR_ENDPOINT", "https://api.cognitive.microsofttranslator.com")
    
    if not key or not location:
         print("❌ Error: AZURE_TRANSLATOR_KEY and AZURE_TRANSLATOR_LOCATION not found in .env")
    else:
        path = '/translate'
        constructed_url = endpoint + path

        params = {
            'api-version': '3.0',
            'to': ['en']  # Translate to English
        }

        headers = {
            'Ocp-Apim-Subscription-Key': key,
            'Ocp-Apim-Subscription-Region': location,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

        body = [{
             'text': 'કેમ છો દુનિયા! હું ખરેખર તમારી કારને બ્લોકની આસપાસ થોડી વાર ચલાવવા માંગુ છું!'
        }]
        
        try:
            print(f"📡 Sending request to {endpoint}...")
            request = requests.post(constructed_url, params=params, headers=headers, json=body)
            response = request.json()
            
            print(json.dumps(response, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': ')))
            
            if isinstance(response, list) and 'translations' in response[0]:
                 print(f"\n✅ Translated: {response[0]['translations'][0]['text']}")
            else:
                 print("\n⚠️ Unexpected response format.")

        except Exception as e:
            print(f"\n❌ Error during test: {e}")

