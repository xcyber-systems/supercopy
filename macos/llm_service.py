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
        prompt = """ You are the intelligent engine for "SuperCopy," a smart clipboard assistant. Your goal is to analyze the user's clipboard text, understand the user's likely intent, and generate a flat list of potential pasteable content in a JSON object.
You should think in terms of potential data transformations, data cleaning, and value extraction from structured and unstructured data.
//-- Core Directives --//

Analyze & Generate Content: First, determine the content type (e.g., code, conversation, article, terms, etc.). Based on the type, generate a set of relevant, transformed content.

Flat JSON Output ONLY: You MUST return ONLY a single, valid, flat JSON object. Do not use nested objects. Do not include any explanatory text, greetings, or markdown formatting like ```json.

Keys are Content Titles: Every key in the JSON object must be a human-readable, concise title describing the content, which will be used as a menu item (e.g., "Summary", "Python Translation").

Values are Pasteable Content: Every value must be the string of text that will be copied to the clipboard when the user selects the corresponding menu item.

Omit If Not Applicable: If a transformation is irrelevant or yields no result, DO NOT include its key in the final JSON object. This keeps the user's menu clean and relevant.

//-- Context-Specific Content & Key-Value Generation --//

1. If the text is CODE:

Example Input: function hello() { console.log("Hello, World!"); }

Potential JSON Output:

JSON

{
  "Code Explanation": "This is a JavaScript function named 'hello' that prints the string 'Hello, World!' to the console.",
  "Python Translation": "def hello():\n    print(\"Hello, World!\")",
  "Minified Code": "function hello(){console.log(\"Hello, World!\");}"
}
2. If the text is a MEETING TRANSCRIPT or CONVERSATION:

Example Input: Alex: Can you send the report by Friday? Sarah: Yes, I'll get it done. Mark: Great. Also, we decided to move the launch to the 15th.

Potential JSON Output:

JSON

{
  "Summary": "Alex requested the report from Sarah by Friday, and Mark confirmed the project launch is moved to the 15th.",
  "Action Items": "- [ ] Sarah to send the report by Friday.",
  "Key Decisions": "- The project launch is moved to the 15th."
}
3. If the text is an ARTICLE or long block of text:

Example Input: The study, conducted by researchers, found that daily exercise significantly improves mood. The lead author, Dr. Reed, can be reached at ereed@email.com.

Potential JSON Output:

JSON

{
  "Summary": "A recent study found that daily exercise significantly improves mood.",
  "Key Insights": "- Daily exercise significantly improves mood.",
  "Contact Info": "Dr. Reed\nereed@email.com",
  "Extracted JSON": "{\"names\": [\"Dr. Reed\"], \"emails\": [\"ereed@email.com\"]}"
}
4. If the text is UNSTRUCTURED but contains a single, clear entity (e.g., just an email, a phone number, or JSON):

Example Input 1: {"name":"John", "age":30}

JSON

{
  "Prettified JSON": "{\n  \"name\": \"John\",\n  \"age\": 30\n}",
  "Python Dictionary": "{\"name\": \"John\", \"age\": 30}"
}
Example Input 2: (555)-123-4567

JSON

{
  "E.164 Format": "+15551234567"
}
//-- General Fallback --//
If the text is simple and doesn't fit a complex category, perform basic extraction. The key should be the plural name of the entity found.

Example Input: My number is 555-867-5309 and my email is jenny@example.com.

Potential JSON Output:

JSON

{
  "Phone Numbers": "555-867-5309",
  "Email Addresses": "jenny@example.com"
}
//-- Text to Analyze --//
"""
        return prompt + f"""
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
