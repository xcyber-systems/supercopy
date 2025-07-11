# llm_service.py
import os
import requests
import json
from abc import ABC, abstractmethod
from dotenv import load_dotenv

# The "Interface" - any LLM class we create must follow this structure
class LLMService(ABC):
    @abstractmethod
    def analyze_text(self, text: str) -> dict:
        """
        Analyzes the text and returns a dictionary of extracted information.
        Example return:
        {
            "summary": "A concise summary of the text.",
            "phone_numbers": ["+1-555-123-4567"],
            "emails": ["test@example.com"]
        }
        """
        pass

# A concrete implementation for the Gemini API
class GeminiService(LLMService):
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key for Gemini is missing.")
        self.api_key = api_key
        #self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={self.api_key}"
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"

    def analyze_text(self, text: str) -> dict:
        prompt = self._build_prompt(text)

        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "response_mime_type": "application/json",
            }
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=15)
            response.raise_for_status()  # Raise an exception for bad status codes
            result_text = response.json()['candidates'][0]['content']['parts'][0]['text']
            print(result_text)
            return json.loads(result_text)
        except requests.exceptions.RequestException as e:
            print(f"API Request Error: {e}")
            return {"error": "Failed to connect to API."}
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"API Response Parsing Error: {e}")
            return {"error": "Could not parse API response."}

    def _build_prompt(self, text: str) -> str:
        # This prompt is key. It instructs the LLM to return structured JSON.
        return f"""
        You are an expert at analyzing text and extracting key features. Analyze the following text.
        - Identify key features to extract in the text (eg. phone numbers, emails, names, links, dates, etc.).
        - Extract the all the entities in the text for every key feature identified in the text
        - return ONLY a valid JSON object. Do not include any other text or formatting like markdown ```json.
        - Do not include any other text or formatting like markdown ```json.

        The JSON object should have the following keys at minimum:
        - "summary": A concise, one-sentence summary.
        The JSON object should have other keys based on the key features identified in the text:
        Examples:
        - "phone_numbers": A list of all phone numbers found.
        - "emails": A list of all email addresses found.
        - "names": A list of all names found.
        - "links": A list of all links found.
        - "dates": A list of all dates found.
        - "numbers": A list of all numbers found.
        - "times": A list of all times found.
        - "addresses": A list of all addresses found.
        - "cities": A list of all cities found.
        - "states": A list of all states found.
        - "Components": A list of all components found.

        If a key has no results, return an empty list or an empty string.

        Text to analyze:
        ---
        {text}
        ---
        """

# This function allows the main app to get a service without knowing the details
def get_llm_service(api_key: str = None) -> LLMService:
    # We could add logic here to choose between different services
    # For the MVP, we will use Gemini.
    if not api_key:
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("API key is required. Either pass it directly or set GEMINI_API_KEY environment variable.")

    return GeminiService(api_key=api_key)
