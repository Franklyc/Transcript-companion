import os
import tkinter as tk
from tkinter import filedialog
import pyperclip

def get_latest_file(directory):
    files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    if not files:
        return None
    latest_file = max(files, key=os.path.getmtime)
    return latest_file

def select_folder(folder_var):
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_var.set(folder_path)

def copy_to_clipboard(text):
    pyperclip.copy(text)