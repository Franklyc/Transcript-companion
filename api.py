import openai
import config
from PyQt6.QtWidgets import QApplication
import tkinter as tk

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
                api_key=config.CEREBRAS_API_KEY
            )
            model_name = model_name.replace("[Cerebras] ", "")
            params["max_completion_tokens"] = 8192
            
        elif model_name.startswith("[Groq]"):
            client = openai.OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=config.GROQ_API_KEY
            )
            model_name = model_name.replace("[Groq] ", "")
            params["max_tokens"] = 32768 if model_name == "mixtral-8x7b-32768" else 8000

        elif model_name.startswith("[Gemini]"):
            client = openai.OpenAI(
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                api_key=config.GEMINI_API_KEY
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
                api_key=config.SAMBANOVA_API_KEY
            )
            model_name = model_name.replace("[SambaNova] ", "")
            params["model"] = model_name

        elif model_name.startswith("[LMstudio]"):
            client = openai.OpenAI(
                base_url="http://localhost:1234/v1",
                api_key=config.LMSTUDIO_API_KEY
            )
            model_name = model_name.replace("[LMstudio] ", "")
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
        output_textbox.insertPlainText(f"调用模型失败: {e}")
        QApplication.processEvents()