# SuperCopy - Context-Aware Copy-Paste Tool for macOS

A macOS menu bar application that monitors your clipboard and provides context-aware actions using AI analysis.

## Features

- **Menu Bar Integration**: Runs quietly in your macOS menu bar
- **Clipboard Monitoring**: Automatically detects new clipboard content
- **AI-Powered Analysis**: Uses LLM to extract summaries, phone numbers, and emails
- **Dynamic Menu**: Context-aware menu options based on clipboard content
- **Model Agnostic**: Easy to swap between different LLM providers

## Setup

### 1. Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Dependencies are already installed, but if needed:
pip install rumps pyperclip requests python-dotenv py2app
```

### 2. Configure API Key

Edit the `.env` file and add your Gemini API key:

```
GEMINI_API_KEY="your_actual_api_key_here"
```

Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

### 3. Run the Application

```bash
# For development
source venv/bin/activate
python3 app.py
```

### 4. Build Standalone App

```bash
# Development build (faster)
source venv/bin/activate
python3 setup.py py2app -A

# Production build (for distribution)
python3 setup.py py2app
```

The built app will be in the `dist/` folder and can be moved to `/Applications/`.

## Usage

1. Launch the app - you'll see a 📋 icon in your menu bar
2. Copy any text to your clipboard
3. The icon will briefly change to ✨ while processing
4. Click the menu bar icon to see context-aware options:
   - **Paste Summary**: AI-generated summary of the text
   - **Paste Phone Numbers**: Extracted phone numbers
   - **Paste Emails**: Extracted email addresses
   - **Original**: The original copied text

## Project Structure

```
supercopy/
├── app.py              # Main application
├── llm_service.py      # Model-agnostic LLM service
├── setup.py            # py2app packaging configuration
├── .env                # Environment variables (API keys)
├── .gitignore          # Git ignore file
├── venv/               # Virtual environment
└── README.md           # This file
```

## Extending with Other LLM Providers

To add support for other LLM providers (OpenAI, Anthropic, etc.), create a new class in `llm_service.py` that implements the `LLMService` interface:

```python
class OpenAIService(LLMService):
    def __init__(self, api_key: str):
        # Initialize with OpenAI API key
        pass
    
    def analyze_text(self, text: str) -> dict:
        # Implement OpenAI API call
        pass
```

Then update the `get_llm_service()` function to return your preferred provider.

## Troubleshooting

- **Permission Issues**: macOS may require accessibility permissions for clipboard monitoring
- **API Errors**: Check your API key in the `.env` file
- **Build Issues**: Make sure all dependencies are installed in the virtual environment

## License

This project is for educational and development purposes.