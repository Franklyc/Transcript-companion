#deprecated in favor of qt_gui
import tkinter as tk
from tkinter import ttk, filedialog
import config
import utils
import api
import pyperclip
import prefix
from lang import STRINGS

def copy_latest_file_content(label, output_textbox, model_var, temperature_var, folder_var, custom_prefix_textbox, custom_suffix_textbox, lang):
    directory = folder_var.get() or config.DEFAULT_FOLDER_PATH
    latest_file = utils.get_latest_file(directory)
    original_prefix = prefix.get_original_prefix()

    custom_prefix = custom_prefix_textbox.get("1.0", "end").strip()
    custom_suffix = custom_suffix_textbox.get("1.0", "end").strip()

    if latest_file:
        try:
            with open(latest_file, 'r', encoding='utf-8') as file:
                content = file.read()
            combined_content = f"{original_prefix}\n{custom_prefix}\n{content}\n{custom_suffix}"
            utils.copy_to_clipboard(combined_content)
            label.config(text=f"{STRINGS[lang]['copied_success']}\n{STRINGS[lang]['file_path']}{latest_file}", fg="green")
            api.fetch_model_response(combined_content, output_textbox, model_var.get(), temperature_var.get())

        except Exception as e:
            label.config(text=f"{STRINGS[lang]['read_file_error']}{e}", fg="red")
    else:
        label.config(text=STRINGS[lang]['no_files_available'], fg="red")

def update_language(lang, window, *elements):
    window.title(STRINGS[lang]['window_title'])
    [folder_label, model_label, temp_label, prefix_label, suffix_label, copy_button, select_button] = elements
    
    folder_label.config(text=STRINGS[lang]['current_folder'])
    model_label.config(text=STRINGS[lang]['select_model'])
    temp_label.config(text=STRINGS[lang]['set_temperature'])
    prefix_label.config(text=STRINGS[lang]['custom_prefix'])
    suffix_label.config(text=STRINGS[lang]['custom_suffix'])
    copy_button.config(text=STRINGS[lang]['copy_and_get_answer'])
    select_button.config(text=STRINGS[lang]['select_folder'])

def create_gui():
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    window = tk.Tk()
    window.title(STRINGS['zh']['window_title'])
    window.geometry("800x800")
    window.resizable(False, False)
    window.configure(bg="#F0F0F0")

    frame = ttk.Frame(window)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Language selector
    lang_var = tk.StringVar(value='zh')
    lang_frame = ttk.Frame(frame)
    lang_frame.grid(row=0, column=0, columnspan=3, pady=5)
    ttk.Radiobutton(lang_frame, text="中文", variable=lang_var, value='zh').pack(side=tk.LEFT, padx=5)
    ttk.Radiobutton(lang_frame, text="English", variable=lang_var, value='en').pack(side=tk.LEFT, padx=5)

    folder_var = tk.StringVar(value=config.DEFAULT_FOLDER_PATH)
    folder_label = ttk.Label(frame, text=STRINGS['zh']['current_folder'])
    folder_label.grid(row=1, column=0, sticky="w", pady=5)
    folder_display = ttk.Entry(frame, textvariable=folder_var, width=50, state="readonly")
    folder_display.grid(row=1, column=1, pady=5, padx=5)
    select_button = ttk.Button(frame, text=STRINGS['zh']['select_folder'], command=lambda: utils.select_folder(folder_var))
    select_button.grid(row=1, column=2, pady=5, padx=5)

    model_var = tk.StringVar(value=config.DEFAULT_MODEL)
    model_label = ttk.Label(frame, text=STRINGS['zh']['select_model'])
    model_label.grid(row=2, column=0, sticky="w", pady=5)
    model_combo = ttk.Combobox(
        frame, textvariable=model_var, values=config.AVAILABLE_MODELS, state="readonly", width=30
    )
    model_combo.grid(row=2, column=1, pady=5, padx=5)

    temperature_var = tk.StringVar(value=config.DEFAULT_TEMPERATURE)
    temperature_label = ttk.Label(frame, text=STRINGS['zh']['set_temperature'])
    temperature_label.grid(row=3, column=0, sticky="w", pady=5)
    temperature_entry = ttk.Entry(frame, textvariable=temperature_var, width=10)
    temperature_entry.grid(row=3, column=1, pady=5, padx=5)

    custom_prefix_label = ttk.Label(frame, text=STRINGS['zh']['custom_prefix'])
    custom_prefix_label.grid(row=4, column=0, sticky="nw", pady=5)
    custom_prefix_textbox = tk.Text(frame, height=3, wrap=tk.WORD, font=("Microsoft YaHei", 10))
    custom_prefix_textbox.grid(row=4, column=1, columnspan=2, pady=5, sticky="nsew")

    custom_suffix_label = ttk.Label(frame, text=STRINGS['zh']['custom_suffix'])
    custom_suffix_label.grid(row=5, column=0, sticky="nw", pady=5)
    custom_suffix_textbox = tk.Text(frame, height=3, wrap=tk.WORD, font=("Microsoft YaHei", 10))
    custom_suffix_textbox.grid(row=5, column=1, columnspan=2, pady=5, sticky="nsew")

    confirmation_label = tk.Label(frame, text="", fg="green", bg="#F0F0F0", font=("Microsoft YaHei", 10))
    confirmation_label.grid(row=6, column=0, columnspan=3, sticky="w", pady=5)

    output_textbox = tk.Text(frame, wrap=tk.WORD, font=("Microsoft YaHei", 10), height=20)
    output_textbox.grid(row=7, column=0, columnspan=3, pady=5, padx=5, sticky="nsew")

    scrollbar = ttk.Scrollbar(frame, command=output_textbox.yview)
    scrollbar.grid(row=7, column=3, sticky="ns")
    output_textbox.config(yscrollcommand=scrollbar.set)

    copy_button = tk.Button(
        frame, text=STRINGS['zh']['copy_and_get_answer'], bg="#0078D7", fg="white", font=("Segoe UI", 12),
        activebackground="#005A9E", activeforeground="white",
        command=lambda: copy_latest_file_content(confirmation_label, output_textbox, model_var, temperature_var, folder_var, custom_prefix_textbox, custom_suffix_textbox, lang_var.get())
    )
    copy_button.grid(row=8, column=0, columnspan=3, pady=10)

    # Store labels and buttons that need language updates
    elements = [folder_label, model_label, temperature_label, custom_prefix_label, 
                custom_suffix_label, copy_button, select_button]
    
    # Bind language change
    lang_var.trace('w', lambda *args: update_language(lang_var.get(), window, *elements))

    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(7, weight=1)

    window.mainloop()