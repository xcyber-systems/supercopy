import json
from llm_service import GeminiService

def extract_features(text: str, llm_service: GeminiService) -> dict:
    """Extracts features from text using the provided LLM service."""
    return llm_service.analyze_text(text)

if __name__ == "__main__":
    # This block is for demonstrating the llm_handler.py as a standalone script.
    api_key = input("Please enter your Gemini API Key: ")
    if not api_key:
        print("API key is required to run this demonstration.")
    else:
        try:
            gemini_service = GeminiService(api_key)
            sample_text = "John Doe, a software engineer, can be reached at john.doe@email.com or 555-123-4567. His colleague, Jane Smith (jane.s@workplace.net), is also on the project. The project kickoff is tomorrow."
            print(f"Analyzing text: \"{sample_text}\"")
            extracted_data = extract_features(sample_text, gemini_service)
            print("\nExtracted Data:")
            print(json.dumps(extracted_data, indent=2))
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
