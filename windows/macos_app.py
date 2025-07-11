# app.py - Final Version
import rumps
import pyperclip
import json
import os
from llm_service import get_llm_service
from functools import partial

class LlmCopyPasteApp(rumps.App):
    def __init__(self):
        super(LlmCopyPasteApp, self).__init__("📋")
        self.config_file = os.path.expanduser("~/.supercopy_config.json")
        self.llm_service = None
        self.last_clipboard_content = ""
        self.is_paused = False  # Track pause state

        # Load API key and initialize service
        self.load_config()
        if not self.api_key:
            self.show_settings_dialog(None)
        else:
            self.initialize_llm_service()

        # Initialize menu properly
        self.update_menu({"info": "Copy some text to start..."} if self.llm_service else {"error": "Please configure API key in Settings"})

        # Run first check on startup
        self.check_clipboard(None)

    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.api_key = config.get("gemini_api_key", "")
            else:
                self.api_key = ""
        except Exception as e:
            print(f"Error loading config: {e}")
            self.api_key = ""

    def save_config(self):
        """Save configuration to file"""
        try:
            config = {"gemini_api_key": self.api_key}
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving config: {e}")

    def initialize_llm_service(self):
        """Initialize the LLM service with the API key"""
        try:
            from llm_service import GeminiService
            self.llm_service = GeminiService(self.api_key)
        except Exception as e:
            print(f"Error initializing LLM service: {e}")
            self.llm_service = None

    def show_settings_dialog(self, _):
        """Show a dialog to enter API key"""
        response = rumps.Window(
            message="Enter your Gemini API Key:",
            title="SuperCopy Settings",
            default_text=self.api_key if hasattr(self, 'api_key') else "",
            cancel=True,
            dimensions=(320, 160)
        ).run()

        if response.clicked:
            self.api_key = response.text.strip()
            if self.api_key:
                self.save_config()
                self.initialize_llm_service()
                rumps.notification("Settings Saved", "API key has been saved successfully.", "")
            else:
                rumps.notification("Warning", "API key cannot be empty.", "")
        else:
            if not hasattr(self, 'api_key') or not self.api_key:
                rumps.notification("Warning", "SuperCopy needs an API key to function.", "")

    @rumps.timer(1)
    def check_clipboard(self, _):
        if self.is_paused:
            return

        current_clipboard = pyperclip.paste().strip()
        # Process only if clipboard is not empty and has new content
        if current_clipboard and current_clipboard != self.last_clipboard_content:
            self.title = "✨"  # Indicate processing
            self.last_clipboard_content = current_clipboard
            self.process_text(current_clipboard)

    def toggle_pause(self, _):
        """Toggle pause/resume state for clipboard monitoring"""
        self.is_paused = not self.is_paused

        if self.is_paused:
            self.title = "⏸️"  # Paused icon
            rumps.notification("SuperCopy Paused", "Clipboard monitoring is now paused", "")
        else:
            self.title = "📋"  # Normal icon
            rumps.notification("SuperCopy Resumed", "Clipboard monitoring is now active", "")

        # Update menu to reflect new state
        if hasattr(self, 'last_menu_data'):
            self.update_menu(self.last_menu_data)
        else:
            self.update_menu({"info": "Copy some text to start..."} if self.llm_service else {"error": "Please configure API key in Settings"})

    def process_text(self, text):
        if not self.llm_service:
            self.update_menu({"error": "LLM service not initialized. Please check settings."})
            return

        extracted_data = self.llm_service.analyze_text(text)
        self.update_menu(extracted_data)
        self.title = "📋"  # Reset icon

    def update_menu(self, data: dict):
        self.menu.clear()
        self.last_menu_data = data  # Store for refresh when toggling pause

        # Add pause/resume button at the top
        pause_text = "Resume Monitoring" if self.is_paused else "Pause Monitoring"
        self.menu.add(rumps.MenuItem(pause_text, callback=self.toggle_pause))
        self.menu.add(rumps.separator)

        if not data or "error" in data:
            self.menu.add(f"Error: {data.get('error', 'Unknown')}")
            self.menu.add(rumps.MenuItem("Copy some text to start..."))
            # Add settings menu even on error
            self.menu.add(rumps.separator)
            self.menu.add(rumps.MenuItem("Settings", callback=self.show_settings_dialog))
            self.menu.add(rumps.separator)
            self.menu.add(rumps.MenuItem("Quit", callback=self.quit_app))
            return

        if "info" in data:
            self.menu.add(data.get('info', 'Ready...'))
            self.menu.add(rumps.separator)
            self.menu.add(rumps.MenuItem("Settings", callback=self.show_settings_dialog))
            self.menu.add(rumps.separator)
            self.menu.add(rumps.MenuItem("Quit", callback=self.quit_app))
            return

        # Dynamically create menu items for each key in the data
        for key, value in data.items():
            if key == "error":  # Skip error key if present
                continue

            if not value:  # Skip empty values (empty lists, empty strings, None, etc.)
                continue

            if isinstance(value, list):
                if len(value) > 0:
                    # For lists, join items and show preview + count
                    all_items = ", ".join(str(item) for item in value)
                    preview = all_items[:30] + "..." if len(all_items) > 30 else all_items
                    menu_label = f"Paste All {key.replace('_', ' ').title()} ({len(value)}): {preview}"
                    menu_item = rumps.MenuItem(
                        menu_label,
                        callback=partial(self.copy_to_clipboard, all_items)
                    )
                    self.menu.add(menu_item)
            elif isinstance(value, str):
                # For strings, show truncated preview
                preview = value[:30] + "..." if len(value) > 30 else value
                menu_label = f"Paste {key.replace('_', ' ').title()}: {preview}"
                menu_item = rumps.MenuItem(
                    menu_label,
                    callback=partial(self.copy_to_clipboard, value)
                )
                self.menu.add(menu_item)
            else:
                # For other types, convert to string and show preview
                value_str = str(value)
                preview = value_str[:30] + "..." if len(value_str) > 30 else value_str
                menu_label = f"Paste {key.replace('_', ' ').title()}: {preview}"
                menu_item = rumps.MenuItem(
                    menu_label,
                    callback=partial(self.copy_to_clipboard, value_str)
                )
                self.menu.add(menu_item)

        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem(f"Original: {self.last_clipboard_content[:30]}...", callback=partial(self.copy_to_clipboard, self.last_clipboard_content)))
        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem("Settings", callback=self.show_settings_dialog))
        self.menu.add(rumps.MenuItem("Quit", callback=self.quit_app))

    def copy_to_clipboard(self, content: str, _):
        pyperclip.copy(content)
        rumps.notification("Copied!", "Content is now on your clipboard.", "")

    def quit_app(self, _):
        rumps.quit_application()


if __name__ == "__main__":
    app = LlmCopyPasteApp()
    app.run()
