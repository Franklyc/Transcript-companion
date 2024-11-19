import os
import tkinter as tk
from tkinter import ttk
import pyperclip
from cerebras.cloud.sdk import Cerebras

def get_latest_file(directory):
    """获取指定目录下最新修改的文件"""
    files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    if not files:
        return None
    latest_file = max(files, key=os.path.getmtime)
    return latest_file

def fetch_model_response(prompt, output_label, model_name, temperature):
    """使用 Cerebras API 调用模型并显示响应"""
    try:
        client = Cerebras(api_key=os.environ.get("CEREBRAS_API_KEY"))

        stream = client.chat.completions.create(
            messages=[
                {"role": "system", "content": ""},
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": ""}
            ],
            model=model_name,
            stream=True,
            max_completion_tokens=8192,
            temperature=float(temperature),
            top_p=1
        )
        # 实时更新响应到窗口
        response = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            response += delta
            output_label.config(text=response)
            output_label.update()
    except Exception as e:
        output_label.config(text=f"调用模型失败: {e}", fg="red")

def copy_latest_file_content(label, output_label, model_var, temperature_var):
    """复制最新文件的内容到剪贴板，并在窗口中显示确认信息和模型回答"""
    directory = r"C:\Users\Lingyun Chen\OneDrive\文档\TMSpeechLogs"  # 指定路径
    latest_file = get_latest_file(directory)

    prefix = (
        "以下是我的会议转录文字（可能因识别而存在部分错误），请你结合上下文，精准的判断出对方最新的要求或提问，并给出回答的范例。只要回答对方最新的要求或提问即可。\n\n"
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

    if latest_file:
        try:
            with open(latest_file, 'r', encoding='utf-8') as file:
                content = file.read()
            combined_content = prefix + content
            pyperclip.copy(combined_content)
            label.config(text=f"已复制最新文件内容！\n文件路径: {latest_file}", fg="green")

            # 调用模型获取回答
            fetch_model_response(combined_content, output_label, model_var.get(), temperature_var.get())

        except Exception as e:
            label.config(text=f"读取文件失败: {e}", fg="red")
    else:
        label.config(text="目录中没有可用的文件！", fg="red")

# 创建 GUI 界面
def create_gui():
    """创建 GUI 界面"""
    window = tk.Tk()
    window.title("TMSpeech Companion")
    window.geometry("600x500")
    window.resizable(False, False)
    window.configure(bg="#F0F0F0")  # Windows 10 默认浅灰背景

    # 模型选择
    model_var = tk.StringVar(value="llama3.1-70b")  # 默认模型
    model_label = ttk.Label(window, text="选择模型:")
    model_label.pack(pady=5)
    model_combo = ttk.Combobox(
        window, textvariable=model_var, values=["llama3.1-70b", "llama3.1-8b"], state="readonly" # Add more models as needed
    )
    model_combo.pack(pady=5)
    model_combo.pack(pady=5)

    # 温度设置
    temperature_var = tk.StringVar(value="1.0")
    temperature_label = ttk.Label(window, text="设置温度 (0.0-1.5):")
    temperature_label.pack(pady=5)
    temperature_entry = ttk.Entry(window, textvariable=temperature_var, width=10)
    temperature_entry.pack(pady=5)

    # 标签
    label = tk.Label(window, text="点击按钮复制最新记事本的内容", bg="#F0F0F0", fg="#000000", font=("Segoe UI", 12))
    label.pack(pady=10)

    # 确认信息标签
    confirmation_label = tk.Label(window, text="", bg="#F0F0F0", fg="green", font=("Segoe UI", 10), wraplength=550)
    confirmation_label.pack(pady=10)

    # 模型输出标签
    output_label = tk.Label(window, text="模型回答将在这里显示...", bg="#F0F0F0", fg="#000000", font=("Segoe UI", 10), wraplength=550, justify="left")
    output_label.pack(pady=10)

    # 按钮
    copy_button = tk.Button(
        window, text="复制并获取回答", bg="#0078D7", fg="white", font=("Segoe UI", 12),
        activebackground="#005A9E", activeforeground="white",
        command=lambda: copy_latest_file_content(confirmation_label, output_label, model_var, temperature_var)
    )
    copy_button.pack(pady=20, ipadx=10, ipady=5)

    # 运行窗口
    window.mainloop()


if __name__ == "__main__":
    create_gui()
