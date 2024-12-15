import openai
import src.config.config
from PyQt6.QtWidgets import QApplication
import tkinter as tk
from src.gui.lang import STRINGS

def _get_openai_client(model_name):
    if model_name.startswith("[Cerebras]"):
        return openai.OpenAI(
            base_url="https://api.cerebras.ai/v1",
            api_key=src.config.config.CEREBRAS_API_KEY
        ), model_name.replace("[Cerebras] ", "")
    elif model_name.startswith("[Groq]"):
        return openai.OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=src.config.config.GROQ_API_KEY
        ), model_name.replace("[Groq] ", "")
    elif model_name.startswith("[Gemini]"):
        return openai.OpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=src.config.config.GEMINI_API_KEY
        ), model_name.replace("[Gemini] ", "")
    elif model_name.startswith("[SambaNova]"):
        return openai.OpenAI(
            base_url="https://api.sambanova.ai/v1",
            api_key=src.config.config.SAMBANOVA_API_KEY
        ), model_name.replace("[SambaNova] ", "")
    elif model_name.startswith("[Zhipu]"):
        return openai.OpenAI(
            base_url="https://open.bigmodel.cn/api/paas/v4/",
            api_key=src.config.config.ZHIPUAI_API_KEY
        ), model_name.replace("[Zhipu] ", "")
    elif model_name.startswith("[LMstudio]"):
        return openai.OpenAI(
            base_url="http://localhost:1234/v1",
            api_key=src.config.config.LMSTUDIO_API_KEY
        ), model_name.replace("[LMstudio] ", "")
    elif model_name.startswith("[Kobold]"):
        return openai.OpenAI(
            base_url="http://localhost:5001/v1",
            api_key=src.config.config.KOBOLD_API_KEY
        ), model_name.replace("[Kobold] ", "")
    elif model_name.startswith("[Ollama]"):
        return openai.OpenAI(
            base_url="http://localhost:11434/v1",
            api_key=src.config.config.OLLAMA_API_KEY
        ), model_name.replace("[Ollama] ", "")
    elif model_name.startswith("[GLHF]"):
        return openai.OpenAI(
            api_key=src.config.config.GLHF_API_KEY,
            base_url="https://glhf.chat/api/openai/v1",
        ), model_name.replace("[GLHF] ", "")
    elif model_name.startswith("[SiliconFlow]"):
        return openai.OpenAI(
            base_url="https://api.siliconflow.cn/v1",
            api_key=src.config.config.SILICONFLOW_API_KEY
        ), model_name.replace("[SiliconFlow] ", "")
    else:
        return None, model_name

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

        client, model_name = _get_openai_client(model_name)
        if client is None:
            params["model"] = model_name
            client = openai.OpenAI() # default client
        else:
            params["model"] = model_name

        if model_name.startswith("gemini"):
            response = client.chat.completions.create(**params)
            output_textbox.clear()
            for chunk in response:
                delta = chunk.choices[0].delta.content or ""
                output_textbox.insertPlainText(delta)
                QApplication.processEvents()
            return
        
        if model_name.startswith("cerebras"):
            params["max_completion_tokens"] = 8192

        stream = client.chat.completions.create(**params)

        output_textbox.clear()
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            output_textbox.insertPlainText(delta)
            QApplication.processEvents()

    except Exception as e:
        output_textbox.clear()
        main_window = QApplication.instance().activeWindow()
        lang = main_window.current_lang if main_window else 'zh'
        output_textbox.insertPlainText(f"{STRINGS[lang]['model_call_error']}{e}")
        QApplication.processEvents()
