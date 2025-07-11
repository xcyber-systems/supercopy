import tkinter as tk
from tkinter import simpledialog, messagebox

def settings_dialog_process(current_key, queue):
    root = tk.Tk()
    root.withdraw()
    new_key = simpledialog.askstring("SuperCopy Settings", "Enter your Gemini API Key:", initialvalue=current_key, parent=root)
    if new_key is not None:
        queue.put(new_key.strip())
        messagebox.showinfo("Settings Saved", "API key has been saved successfully.")
    else:
        queue.put(None)
    root.destroy()
