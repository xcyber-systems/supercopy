# SuperCopy - Context-Aware Copy-Paste Tool for Windows

A Windows system tray application that monitors your clipboard and provides context-aware actions using AI analysis.

## Features

- **System Tray Integration**: Runs quietly in your Windows system tray
- **Clipboard Monitoring**: Automatically detects new clipboard content
- **AI-Powered Analysis**: Uses LLM to extract summaries, phone numbers, and emails
- **Dynamic Menu**: Context-aware menu options based on clipboard content
- **Model Agnostic**: Easy to swap between different LLM providers

## Setup

### 1. Install Dependencies

```bash
# Activate virtual environment (if you have one)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key

Your Gemini API Key can be configured directly within the application's settings dialog.

### 3. Run the Application

```bash
# For development
venv\Scripts\activate
python app.py
```

### 4. Build Standalone App

To create a standalone executable for Windows, use PyInstaller.

```bash
# First, install PyInstaller if you haven't already
pip install pyinstaller

# Navigate to the directory containing supercopy.spec
# cd C:\Users\steve\Documents\Projects\supercopy\windows

# Build the application using the spec file
pyinstaller supercopy.spec
```

The built executable (`SuperCopy.exe`) will be found in the `dist` folder.

## Usage

1. Launch the app - you'll see a blue square icon (or your custom icon) in your system tray.
2. Copy any text to your clipboard.
3. The icon may briefly change or a notification might appear while processing.
4. Right-click the system tray icon to see context-aware options:
   - **Paste Summary**: AI-generated summary of the text
   - **Paste Phone Numbers**: Extracted phone numbers
   - **Paste Emails**: Extracted email addresses
   - **Original**: The original copied text

## Project Structure

```
windows/
├── app.py              # Main application
├── llm_service.py      # Model-agnostic LLM service
├── ui_manager.py       # UI abstraction for Windows
├── requirements.txt    # Python dependencies
├── supercopy.spec      # PyInstaller configuration
├── icon.ico            # Application icon
├── venv/               # Virtual environment
└── README.md           # This file
```

## Troubleshooting

- **API Errors**: Check your API key in the in-app settings.
- **Build Issues**: Ensure all dependencies are installed and PyInstaller is correctly configured.

## License

This project is for educational and development purposes.
