import openai
import config
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

            output_textbox.delete(1.0, tk.END)
            for chunk in response:
                delta = chunk.choices[0].delta.content or ""
                output_textbox.insert(tk.END, delta)
                output_textbox.update()
            return

        params["model"] = model_name
        stream = client.chat.completions.create(**params)

        output_textbox.delete(1.0, tk.END)
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            output_textbox.insert(tk.END, delta)
            output_textbox.update()

    except Exception as e:
        output_textbox.delete(1.0, tk.END)
        output_textbox.insert(tk.END, f"调用模型失败: {e}")