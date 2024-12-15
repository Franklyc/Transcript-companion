import openai
import src.config.config
from PyQt6.QtWidgets import QApplication
import tkinter as tk
from src.gui.lang import STRINGS

def fetch_model_response(prompt, output_textbox, model_name, temperature):
    try:
        params = {
            "messages": [
                {"role": "system", "content": ""},
                {"role": "user", "content": prompt},
            ],
            "stream": True,
            "temperature": float(temperature),
            "top_p": 1
        }

        if model_name.startswith("[Cerebras]"):
            client = openai.OpenAI(
                base_url="https://api.cerebras.ai/v1",
                api_key=src.config.config.CEREBRAS_API_KEY
            )
            model_name = model_name.replace("[Cerebras] ", "")
            params["max_completion_tokens"] = 8192
            
        elif model_name.startswith("[Groq]"):
            client = openai.OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=src.config.config.GROQ_API_KEY
            )
            model_name = model_name.replace("[Groq] ", "")

        elif model_name.startswith("[Gemini]"):
            client = openai.OpenAI(
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                api_key=src.config.config.GEMINI_API_KEY
            )
            model_name = model_name.replace("[Gemini] ", "")
            params["model"] = model_name
            response = client.chat.completions.create(**params)

            output_textbox.clear()
            for chunk in response:
                delta = chunk.choices[0].delta.content or ""
                output_textbox.insertPlainText(delta)
                QApplication.processEvents()  # 保留事件处理
            return
            
        elif model_name.startswith("[SambaNova]"):
            client = openai.OpenAI(
                base_url="https://api.sambanova.ai/v1",
                api_key=src.config.config.SAMBANOVA_API_KEY
            )
            model_name = model_name.replace("[SambaNova] ", "")
            params["model"] = model_name

        elif model_name.startswith("[LMstudio]"):
            client = openai.OpenAI(
                base_url="http://localhost:1234/v1",
                api_key=src.config.config.LMSTUDIO_API_KEY
            )
            model_name = model_name.replace("[LMstudio] ", "")
            params["model"] = model_name

        elif model_name.startswith("[Kobold]"):
            client = openai.OpenAI(
                base_url="http://localhost:5001/v1",
                api_key=src.config.config.KOBOLD_API_KEY
            )
            model_name = model_name.replace("[Kobold] ", "")
            params["model"] = model_name

        elif model_name.startswith("[Ollama]"):
            client = openai.OpenAI(
                base_url="http://localhost:11434/v1",
                api_key=src.config.config.OLLAMA_API_KEY
            )
            model_name = model_name.replace("[Ollama] ", "")
            params["model"] = model_name

        params["model"] = model_name
        stream = client.chat.completions.create(**params)

        output_textbox.clear()
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            output_textbox.insertPlainText(delta)
            QApplication.processEvents()  # 保留事件处理

    except Exception as e:
        output_textbox.clear()
        main_window = QApplication.instance().activeWindow()
        lang = main_window.current_lang if main_window else 'zh'
        output_textbox.insertPlainText(f"{STRINGS[lang]['model_call_error']}{e}")
        QApplication.processEvents()
