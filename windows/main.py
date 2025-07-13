
import time
import pyperclip
from PIL import Image, ImageDraw
from pystray import Icon as icon, Menu as menu, MenuItem as item
import threading
import json
import os
import tkinter as tk
from tkinter import simpledialog, messagebox
from functools import partial
from llm_handler import extract_features
from llm_service import GeminiService
import multiprocessing
from settings_app import settings_dialog_process

# --- Global State ---
CONFIG_FILE = os.path.expanduser("~/.supercopy_config.json")
extracted_data = {}
last_text = ""
llm_service = None
is_paused = False
api_key = None
tray_icon = None

# --- Secret Detection ---
def detect_secrets(text):
    """Detect if text contains sensitive information like passwords"""
    # Simple rule: if it's a single string with no spaces and under 30 characters,
    # it's likely a password or sensitive token
    text = text.strip()

    # Check if it's a single string with no spaces and under 30 characters
    if len(text) < 30 and ' ' not in text and len(text) > 0:
        return True

    return False

# --- Config Management ---
def load_config():
    global api_key
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                api_key = config.get("gemini_api_key", "")
        except Exception:
            api_key = ""
    else:
        api_key = ""

def save_config():
    global api_key
    try:
        config = {"gemini_api_key": api_key}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
    except Exception as e:
        print(f"Error saving config: {e}")

# --- Icon Creation ---
def load_ico_icon(icon_path="icon.ico"):
    """Load icon from ICO file"""
    try:
        return Image.open(icon_path)
    except Exception as e:
        print(f"Error loading icon: {e}")
        # Fallback to a simple colored icon
        return create_fallback_icon()

def create_fallback_icon(color='black'):
    """Create a simple fallback icon"""
    image = Image.new('RGB', (64, 64), color)
    draw = ImageDraw.Draw(image)
    # Draw a simple clipboard-like shape
    draw.rectangle([10, 5, 54, 59], fill='white', outline='black', width=2)
    draw.rectangle([15, 10, 49, 25], fill='lightgray')
    return image

# Load icons from ICO file
try:
    default_icon = load_ico_icon("icon.ico")
    processing_icon = load_ico_icon("icon.ico")  # Same icon for now
    paused_icon = load_ico_icon("icon.ico")      # Same icon for now
except:
    # Fallback to simple icons if ICO loading fails
    default_icon = create_fallback_icon('black')
    processing_icon = create_fallback_icon('blue')
    paused_icon = create_fallback_icon('gray')

# --- Settings Dialog ---
def show_settings_dialog():
    global api_key, llm_service
    queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=settings_dialog_process, args=(api_key, queue))
    p.start()
    p.join()
    result = queue.get() if not queue.empty() else None
    if result:
        api_key = result
        save_config()
        try:
            llm_service = GeminiService(api_key)
        except Exception as e:
            # Optionally show a notification or log error
            pass

# --- Menu Logic ---
def on_exit(tray_icon, item):
    tray_icon.stop()
    os._exit(0)

def on_pause_resume(tray_icon, item):
    global is_paused
    is_paused = not is_paused
    update_tray_menu(tray_icon)
    if is_paused:
        tray_icon.icon = paused_icon
        tray_icon.title = "SuperCopy (Paused)"
    else:
        tray_icon.icon = default_icon
        tray_icon.title = "SuperCopy"

def on_settings(tray_icon, item):
    show_settings_dialog()
    update_tray_menu(tray_icon)

def copy_to_clipboard(value, *args, **kwargs):
    pyperclip.copy(value)
    # Optionally, show a notification (Windows toast notification can be added)

def update_tray_menu(tray_icon):
    global extracted_data, is_paused, last_text
    menu_items = []
    pause_text = "Resume Monitoring" if is_paused else "Pause Monitoring"
    menu_items.append(item(pause_text, lambda icon, item: on_pause_resume(tray_icon, item)))
    menu_items.append(menu.SEPARATOR)
    if not api_key:
        menu_items.append(item("Error: Please configure API key in Settings", lambda: None, enabled=False))
        menu_items.append(menu.SEPARATOR)
        menu_items.append(item("Settings", lambda icon, item: on_settings(tray_icon, item)))
        menu_items.append(item('Exit', lambda icon, item: on_exit(tray_icon, item)))
        tray_icon.menu = menu(*menu_items)
        return
    if not extracted_data:
        menu_items.append(item('Copy some text to start', lambda: None, enabled=False))
    elif "error" in extracted_data:
        menu_items.append(item(f"Error: {extracted_data['error']}", lambda: None, enabled=False))
    elif "warning" in extracted_data:
        menu_items.append(item(extracted_data["warning"], lambda: None, enabled=False))
        menu_items.append(menu.SEPARATOR)
        if last_text:
            menu_items.append(item(f"Original: {last_text[:30]}...", partial(copy_to_clipboard, last_text)))
    elif "info" in extracted_data:
        menu_items.append(item(extracted_data["info"], lambda: None, enabled=False))
    else:
        for key, value in extracted_data.items():
            if key == "error" or not value:
                continue
            if isinstance(value, list) and len(value) > 0:
                all_items = ", ".join(str(item) for item in value)
                preview = all_items[:30] + "..." if len(all_items) > 30 else all_items
                label = f"Paste All {key.replace('_', ' ').title()} ({len(value)}): {preview}"
                menu_items.append(item(label, partial(copy_to_clipboard, all_items)))
            elif isinstance(value, str):
                preview = value[:30] + "..." if len(value) > 30 else value
                label = f"Paste {key.replace('_', ' ').title()}: {preview}"
                menu_items.append(item(label, partial(copy_to_clipboard, value)))
            else:
                value_str = str(value)
                preview = value_str[:30] + "..." if len(value_str) > 30 else value_str
                label = f"Paste {key.replace('_', ' ').title()}: {preview}"
                menu_items.append(item(label, partial(copy_to_clipboard, value_str)))
        menu_items.append(menu.SEPARATOR)
        if last_text:
            menu_items.append(item(f"Original: {last_text[:30]}...", partial(copy_to_clipboard, last_text)))
    menu_items.append(menu.SEPARATOR)
    menu_items.append(item("Settings", lambda icon, item: on_settings(tray_icon, item)))
    menu_items.append(item('Exit', lambda icon, item: on_exit(tray_icon, item)))
    tray_icon.menu = menu(*menu_items)

# --- Background Task ---
def clipboard_monitor(tray_icon):
    global last_text, extracted_data, llm_service, is_paused
    while True:
        if is_paused or not llm_service:
            time.sleep(1)
            continue
        try:
            text = pyperclip.paste()
            if text and text != last_text:
                last_text = text
                tray_icon.icon = processing_icon
                tray_icon.title = "SuperCopy (Processing...)"
                try:
                    # Check for secrets before sending to LLM
                    if detect_secrets(text):
                        extracted_data = {"warning": "Secrets detected: Skipping analysis"}
                        update_tray_menu(tray_icon)
                    else:
                        new_data = extract_features(text, llm_service)
                        if new_data != extracted_data:
                            extracted_data = new_data
                            update_tray_menu(tray_icon)
                except Exception as e:
                    extracted_data = {"error": str(e)}
                    update_tray_menu(tray_icon)
                finally:
                    tray_icon.icon = default_icon
                    tray_icon.title = "SuperCopy"
        except pyperclip.PyperclipException:
            pass
        time.sleep(1)

# --- Main Execution ---
if __name__ == "__main__":
    multiprocessing.freeze_support()
    multiprocessing.set_start_method('spawn', force=True)
    load_config()
    try:
        llm_service = GeminiService(api_key) if api_key else None
    except Exception as e:
        llm_service = None
    initial_menu = menu(
        item('Copy some text to start', lambda: None, enabled=False),
        menu.SEPARATOR,
        item('Settings', lambda icon, item: on_settings(None, item)),
        item('Exit', lambda icon, item: on_exit(None, item))
    )
    tray_icon = icon(
        'SuperCopy',
        default_icon,
        'SuperCopy',
        initial_menu
    )
    def setup(icon):
        icon.visible = True
        monitor_thread = threading.Thread(target=clipboard_monitor, args=(icon,), daemon=True)
        monitor_thread.start()
    update_tray_menu(tray_icon)
    tray_icon.run(setup=setup)
