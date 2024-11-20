import tkinter as tk
from tkinter import ttk, filedialog
import config
import utils
import api
import pyperclip
import prefix

def copy_latest_file_content(label, output_textbox, model_var, temperature_var, folder_var, custom_prefix_textbox, custom_suffix_textbox):
    directory = folder_var.get() or config.DEFAULT_FOLDER_PATH
    latest_file = utils.get_latest_file(directory)

    original_prefix = prefix.get_original_prefix() # Call the function to get the prefix

    custom_prefix = custom_prefix_textbox.get("1.0", "end").strip()
    custom_suffix = custom_suffix_textbox.get("1.0", "end").strip()

    if latest_file:
        try:
            with open(latest_file, 'r', encoding='utf-8') as file:
                content = file.read()
            combined_content = f"{original_prefix}\n{custom_prefix}\n{content}\n{custom_suffix}"
            utils.copy_to_clipboard(combined_content)
            label.config(text=f"已复制最新文件内容！\n文件路径: {latest_file}", fg="green")
            api.fetch_model_response(combined_content, output_textbox, model_var.get(), temperature_var.get())

        except Exception as e:
            label.config(text=f"读取文件失败: {e}", fg="red")
    else:
        label.config(text="目录中没有可用的文件！", fg="red")


def create_gui():
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    window = tk.Tk()
    window.title("TMSpeech Companion")
    window.geometry("800x800")
    window.resizable(False, False)
    window.configure(bg="#F0F0F0")

    frame = ttk.Frame(window)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    folder_var = tk.StringVar(value=config.DEFAULT_FOLDER_PATH)
    folder_label = ttk.Label(frame, text="当前文件夹:")
    folder_label.grid(row=0, column=0, sticky="w", pady=5)
    folder_display = ttk.Entry(frame, textvariable=folder_var, width=50, state="readonly")
    folder_display.grid(row=0, column=1, pady=5, padx=5)
    select_button = ttk.Button(frame, text="选择文件夹", command=lambda: utils.select_folder(folder_var))
    select_button.grid(row=0, column=2, pady=5, padx=5)

    model_var = tk.StringVar(value=config.DEFAULT_MODEL)
    model_label = ttk.Label(frame, text="选择模型:")
    model_label.grid(row=1, column=0, sticky="w", pady=5)
    model_combo = ttk.Combobox(
        frame, textvariable=model_var, values=config.AVAILABLE_MODELS, state="readonly", width=30
    )
    model_combo.grid(row=1, column=1, pady=5, padx=5)

    temperature_var = tk.StringVar(value=config.DEFAULT_TEMPERATURE)
    temperature_label = ttk.Label(frame, text="设置温度 (0.0-1.5):")
    temperature_label.grid(row=2, column=0, sticky="w", pady=5)
    temperature_entry = ttk.Entry(frame, textvariable=temperature_var, width=10)
    temperature_entry.grid(row=2, column=1, pady=5, padx=5)

    custom_prefix_label = ttk.Label(frame, text="自定义前缀:")
    custom_prefix_label.grid(row=3, column=0, sticky="nw", pady=5)
    custom_prefix_textbox = tk.Text(frame, height=3, wrap=tk.WORD, font=("Microsoft YaHei", 10))
    custom_prefix_textbox.grid(row=3, column=1, columnspan=2, pady=5, sticky="nsew")

    custom_suffix_label = ttk.Label(frame, text="自定义后缀:")
    custom_suffix_label.grid(row=4, column=0, sticky="nw", pady=5)
    custom_suffix_textbox = tk.Text(frame, height=3, wrap=tk.WORD, font=("Microsoft YaHei", 10))
    custom_suffix_textbox.grid(row=4, column=1, columnspan=2, pady=5, sticky="nsew")

    confirmation_label = tk.Label(frame, text="", fg="green", bg="#F0F0F0", font=("Microsoft YaHei", 10))
    confirmation_label.grid(row=5, column=0, columnspan=3, sticky="w", pady=5)

    output_textbox = tk.Text(frame, wrap=tk.WORD, font=("Microsoft YaHei", 10), height=20)
    output_textbox.grid(row=6, column=0, columnspan=3, pady=5, padx=5, sticky="nsew")

    scrollbar = ttk.Scrollbar(frame, command=output_textbox.yview)
    scrollbar.grid(row=6, column=3, sticky="ns")
    output_textbox.config(yscrollcommand=scrollbar.set)

    copy_button = tk.Button(
        frame, text="复制并获取回答", bg="#0078D7", fg="white", font=("Segoe UI", 12),
        activebackground="#005A9E", activeforeground="white",
        command=lambda: copy_latest_file_content(confirmation_label, output_textbox, model_var, temperature_var, folder_var, custom_prefix_textbox, custom_suffix_textbox)
    )
    copy_button.grid(row=7, column=0, columnspan=3, pady=10)

    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(6, weight=1)

    window.mainloop()