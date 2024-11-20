import os
import tkinter as tk
from tkinter import ttk, filedialog
import pyperclip
import openai

def get_latest_file(directory):
    """获取指定目录下最新修改的文件"""
    files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    if not files:
        return None
    latest_file = max(files, key=os.path.getmtime)
    return latest_file

def fetch_model_response(prompt, output_textbox, model_name, temperature):
    """使用 OpenAI API 调用模型并显示响应"""
    try:
        # 基础参数
        params = {
            "messages": [
                {"role": "system", "content": ""},
                {"role": "user", "content": prompt},
            ],
            "stream": True,
            "temperature": float(temperature),
            "top_p": 1
        }

        # 根据模型名称确定使用哪个供应商
        if model_name.startswith("[Cerebras]"):
            client = openai.OpenAI(
                base_url="https://api.cerebras.ai/v1",
                api_key=os.environ.get("CEREBRAS_API_KEY")
            )
            model_name = model_name.replace("[Cerebras] ", "")
            params["max_completion_tokens"] = 8192
            
        elif model_name.startswith("[Groq]"):
            client = openai.OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=os.environ.get("GROQ_API_KEY")
            )
            model_name = model_name.replace("[Groq] ", "")
            params["max_tokens"] = 32768 if model_name == "mixtral-8x7b-32768" else 8000

        elif model_name.startswith("[Gemini]"):
            client = openai.OpenAI(
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                api_key=os.environ.get("GEMINI_API_KEY")
            )
            model_name = model_name.replace("[Gemini] ", "")
            params["model"] = model_name
            response = client.chat.completions.create(**params)

            # 实时更新响应到文本框
            output_textbox.delete(1.0, tk.END)  # 清空现有内容
            for chunk in response:
                delta = chunk.choices[0].delta.content or ""
                output_textbox.insert(tk.END, delta)
                # output_textbox.see(tk.END)  # 滚动到最后
                output_textbox.update_idletasks()  # 强制更新GUI
            return

        params["model"] = model_name
        stream = client.chat.completions.create(**params)

        # 实时更新响应到文本框
        output_textbox.delete(1.0, tk.END)  # 清空现有内容
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            output_textbox.insert(tk.END, delta)
            # output_textbox.see(tk.END)  # 滚动到最后
            output_textbox.update_idletasks()  # 强制更新GUI

    except Exception as e:
        output_textbox.delete(1.0, tk.END)
        output_textbox.insert(tk.END, f"调用模型失败: {e}")

def copy_latest_file_content(label, output_textbox, model_var, temperature_var, folder_var, custom_prefix_textbox, custom_suffix_textbox):
    """复制最新文件的内容到剪贴板，并在窗口中显示确认信息和模型回答"""
    directory = folder_var.get() or r"C:\Users\Lingyun Chen\OneDrive\文档\TMSpeechLogs"  # 指定路径
    latest_file = get_latest_file(directory)

    original_prefix = (
        "以下是我的会议转录文字（可能因识别而存在部分错误），请你结合上下文，精准的判断出对方最新的要求或提问，并给出回答的详实可行的范例。只要回答对方最新的要求或提问即可。\n\n"
        "此外，我的简历信息如下，可能与对方的提问有关，如果判定为相关，请结合简历内容进行回答：\n\n"
        "- **教育背景**:\n"
        "  - New York University, Tandon School of Engineering, M.S. Computer Engineering (GPA: 3.56/4.0, 2023-2025预计)\n"
        "  - University of Kentucky, Study Abroad, Electronic Engineering (GPA: 3.56/4.0, Dean's List Spring 2022)\n"
        "  - Beijing University of Technology, B.S. Electronic Science and Technology (GPA: 3.26/4.0)\n\n"
        "- **工作经历**:\n"
        "  - AdaSeco, Customer Support Chatbot Development, AI Engineer (Jul 2024 – Sep 2024)\n"
        "    • Developed a chatbot using LLMs to deliver real-time, context-aware responses for customer support.\n"
        "    • Optimized chatbot response time, reducing latency by 30% during peak traffic, ensuring fast inference and seamless user interactions.\n"
        "    • Collaborated with cross-functional teams to align chatbot capabilities with business goals and user needs.\n"
        "  - Wissee Inc, Graphic Generation Project, AI Engineer (May 2024 – Aug 2024)\n"
        "    • Developed and implemented AIGC models (Text-to-Image and Image-to-Image) to generate over 1,000 unique clothing patterns based on "
        "50+ trending social media topics and top 100 e-commerce products.\n"
        "    • Created a comprehensive pattern database using MySQL with an efficient tagging system, improving search accuracy by 85%, and built a "
        "user-friendly interface in React with an intelligent Q&A system powered by Elasticsearch that reduced query response time by 40%.\n"
        "    • Conducted data analysis on 10,000+ social media posts and 500 e-commerce platforms using Python (Pandas, NumPy).\n"
        "  - Zhongguancun IC Design Park, Arduino IoT Project, Software Developer (Jun 2022 – Jul 2022)\n"
        "    • Spearheaded the design and implementation of an intelligent Arduino-based trolley equipped with line-tracking and ultrasonic obstacle "
        "avoidance capabilities, enhancing its navigational efficiency in dynamic environments.\n"
        "    • Utilized infrared sensors to enable precise line-tracking functionality, allowing the trolley to follow predetermined paths with high accuracy.\n"
        "    • Integrated ultrasonic sensors to implement real-time obstacle detection and avoidance, ensuring smooth and uninterrupted operation of the trolley.\n\n"
        "- **项目经历**:\n"
        "  - Audio Transcription and LLM Response Application Development (July 2024 – Aug 2024)\n"
        "    • Developed a PyQt5 GUI application for recording, transcribing audio (using Groq Whisper models), and generating LLM responses (Google "
        "Gemini API), with custom Text-to-Speech and multithreading for seamless operation.\n"
        "    • Built user authentication, session management (Spring Security), and RESTful APIs, integrating React components for dynamic front-end interaction, deployed to AWS with RDS and App Runner.\n"
        "    • Optimized performance with caching, Docker containerization, conducted API testing with Postman and implemented unit testing for code reliability.\n"
        "  - Automatic Localization of Labyrinth Structure Using YOLOv7 and Python (Dec 2022 – May 2023)\n"
        "    • Adopted the YOLOv7 deep learning model to localize the labyrinth structure from temporal bone CT scans and proved its effectiveness in precise anatomical localization.\n"
        "    • Developed a Python algorithm to automatically generate localization labels from image segmentation results, streamlining model training.\n"
        "    • Conducted comprehensive experiments to validate the effectiveness of the model in achieving precise localization of the labyrinth.\n"
        "  - Detection of Marine Chemical Pollution Based on Machine Learning and Image Processing (Jun 2022 – Aug 2022)\n"
        "    • Assembled a diverse dataset of 800 aerial ocean images, classified into normal and polluted categories for model training.\n"
        "    • Performed image pre-processing in MATLAB, including histogram equalization, contrast enhancement, and dynamic range expansion on RGB/HSV channels to improve image features.\n"
        "    • Developed and tested neural network models in Python, using VGG16 pre-trained model and data augmentation techniques like rotation and flipping.\n"
        "    • Achieved improved accuracy in detecting oil spills by applying dynamic range expansion on the V channel of HSV images.\n\n"
    )

    # 自定义前缀和后缀
    custom_prefix = custom_prefix_textbox.get("1.0", "end").strip()
    custom_suffix = custom_suffix_textbox.get("1.0", "end").strip()

    if latest_file:
        try:
            with open(latest_file, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # 组合文本内容
            combined_content = f"{original_prefix}\n{custom_prefix}\n{content}\n{custom_suffix}"
            pyperclip.copy(combined_content)  # 复制到剪贴板

            # 更新标签
            label.config(text=f"已复制最新文件内容！\n文件路径: {latest_file}", fg="green")

            # 调用模型获取回答
            fetch_model_response(combined_content, output_textbox, model_var.get(), temperature_var.get())

        except Exception as e:
            label.config(text=f"读取文件失败: {e}", fg="red")
    else:
        label.config(text="目录中没有可用的文件！", fg="red")

def select_folder(folder_var):
    """选择文件夹"""
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_var.set(folder_path)

# 创建 GUI 界面
def create_gui():
    """创建 GUI 界面"""
    window = tk.Tk()
    window.title("TMSpeech Companion")
    window.geometry("800x800")
    window.resizable(False, False)
    window.configure(bg="#F0F0F0")  # Windows 10 默认浅灰背景

    # 主框架
    frame = ttk.Frame(window)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # 路径选择
    folder_var = tk.StringVar(value=r"C:\Users\Lingyun Chen\OneDrive\文档\TMSpeechLogs")  # 默认路径
    folder_label = ttk.Label(frame, text="当前文件夹:")
    folder_label.grid(row=0, column=0, sticky="w", pady=5)
    folder_display = ttk.Entry(frame, textvariable=folder_var, width=50, state="readonly")
    folder_display.grid(row=0, column=1, pady=5, padx=5)
    select_button = ttk.Button(frame, text="选择文件夹", command=lambda: select_folder(folder_var))
    select_button.grid(row=0, column=2, pady=5, padx=5)

    # 模型选择
    model_var = tk.StringVar(value="[Cerebras] llama3.1-70b")  # 默认模型
    model_label = ttk.Label(frame, text="选择模型:")
    model_label.grid(row=1, column=0, sticky="w", pady=5)
    model_combo = ttk.Combobox(
        frame, textvariable=model_var, 
        values=[
            "[Cerebras] llama3.1-70b",
            "[Cerebras] llama3.1-8b",
            "[Groq] mixtral-8x7b-32768",
            "[Groq] llama-3.1-70b-versatile",
            "[Groq] llama-3.1-8b-instant",
            "[Groq] llama-3.2-90b-vision-preview",
            "[Gemini] gemini-1.5-flash",
            "[Gemini] gemini-1.5-flash-002",
            "[Gemini] gemini-1.5-flash-8b"
        ], 
        state="readonly",
        width=30  # 调整宽度
    )
    model_combo.grid(row=1, column=1, pady=5, padx=5)

    # 温度设置
    temperature_var = tk.StringVar(value="1.0")
    temperature_label = ttk.Label(frame, text="设置温度 (0.0-1.5):")
    temperature_label.grid(row=2, column=0, sticky="w", pady=5)
    temperature_entry = ttk.Entry(frame, textvariable=temperature_var, width=10)
    temperature_entry.grid(row=2, column=1, pady=5, padx=5)

    # 自定义前缀
    custom_prefix_label = ttk.Label(frame, text="自定义前缀:")
    custom_prefix_label.grid(row=3, column=0, sticky="nw", pady=5)
    custom_prefix_textbox = tk.Text(frame, height=5, wrap=tk.WORD, font=("Microsoft YaHei", 10))
    custom_prefix_textbox.grid(row=3, column=1, columnspan=2, pady=5, sticky="nsew")

    # 自定义后缀
    custom_suffix_label = ttk.Label(frame, text="自定义后缀:")
    custom_suffix_label.grid(row=4, column=0, sticky="nw", pady=5)
    custom_suffix_textbox = tk.Text(frame, height=5, wrap=tk.WORD, font=("Microsoft YaHei", 10))
    custom_suffix_textbox.grid(row=4, column=1, columnspan=2, pady=5, sticky="nsew")

    # 确认信息标签
    confirmation_label = tk.Label(frame, text="", fg="green", bg="#F0F0F0", font=("Microsoft YaHei", 10))
    confirmation_label.grid(row=5, column=0, columnspan=3, sticky="w", pady=5)

    # 文本框
    output_textbox = tk.Text(frame, wrap=tk.WORD, font=("Microsoft YaHei", 10), height=20)
    output_textbox.grid(row=6, column=0, columnspan=3, pady=5, padx=5, sticky="nsew")

    # 滚动条绑定到文本框
    scrollbar = ttk.Scrollbar(frame, command=output_textbox.yview)
    scrollbar.grid(row=6, column=3, sticky="ns")
    output_textbox.config(yscrollcommand=scrollbar.set)

    # 按钮
    copy_button = tk.Button(
        frame, text="复制并获取回答", bg="#0078D7", fg="white", font=("Segoe UI", 12),
        activebackground="#005A9E", activeforeground="white",
        command=lambda: copy_latest_file_content(confirmation_label, output_textbox, model_var, temperature_var, folder_var, custom_prefix_textbox, custom_suffix_textbox)
    )
    copy_button.grid(row=7, column=0, columnspan=3, pady=10)

    # 调整列和行的布局比例
    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(6, weight=1)

    # 运行窗口
    window.mainloop()


if __name__ == "__main__":
    create_gui()
