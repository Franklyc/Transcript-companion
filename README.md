# TMSpeech-companion
[中文版README](README_zh.md)

**A GUI application built with Python/Tkinter that processes speech transcripts using LLM APIs. This tool simplifies the workflow of analyzing and summarizing meeting recordings by leveraging the power of large language models.**

> **Important Note:** This companion tool was specifically created to work with [TMSpeech](https://github.com/jxlpzqc/TMSpeech) v0.0.1-rc3. Due to changes in how transcript history is stored in TMSpeech v0.4.0 and above, this tool is currently not compatible with newer versions.

## Features

* **Folder Selection:** Choose the directory containing your speech transcription files (e.g., `.txt`, `.md`).
* **Multi-LLM Support:** Seamlessly integrate with various LLM providers:
    * **Cerebras** (llama3.1-70b, llama3.1-8b) :sparkles: **FASTEST:** Best choice for quick response times
    * **Groq** (mixtral-8x7b-32768, llama-3.1 models)
    * **Google Gemini** (gemini-1.5-flash models) :books: **LARGEST CONTEXT:** Ideal for long transcripts
    * **Sambanova** (llama-3.1 models, including llama3.1-405B)
* **Temperature Control:** Adjust the temperature parameter (0.0-1.5) to fine-tune the creativity and randomness of the LLM's responses. Lower values result in more focused and deterministic outputs, while higher values encourage more diverse and unexpected generation.
* **Customizable Prefix/Suffix:** Add custom prefix and suffix text to your transcripts before sending them to the LLM. This allows you to provide additional context or instructions to the model, shaping its output to better suit your needs.
* **Real-time Streaming:** View LLM responses in real-time as they are generated, providing immediate feedback and a dynamic interaction with the model.
* **Clipboard Integration:** Easily copy the processed transcript content to the clipboard for use in other applications.
* **Bilingual Support (Chinese/English):** The GUI now supports both Chinese and English. You can switch between languages within the application.

## Requirements

* **Python 3.x**
* The following Python packages:
    * ``tkinter`` (usually included with Python)
    * ``openai``
    * ``pyperclip``

You can install these packages using pip:

```bash
pip install openai pyperclip
```

## Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Franklyc/TMSpeech-companion.git
   ```

2. **Configuration:**

   * **Rename Example Files:** Copy and rename the following files:
      * `config.py.example` to `config.py`
      * `prefix.py.example` to `prefix.py`
   * **API Keys:** Open the newly created `config.py` and replace the placeholder API keys with your actual keys for each LLM provider. These keys are typically obtained from the respective provider's website.
   * **Default Folder:** You can also modify the `DEFAULT_FOLDER_PATH` in `config.py` to point to the directory where your transcripts are stored.
   * **Customize Prefix:** Edit `prefix.py` to modify the `get_original_prefix()` function. This allows you to define the initial instructions or context provided to the LLM before processing each transcript. Provide clear and concise instructions to guide the LLM's response.


3. **Run the Application:**

   ```bash
   python main.py
   ```

## Usage

1. **Select Folder:** Click "Select Folder" and navigate to the directory containing your transcript files.
2. **Choose Model:** Select your desired LLM model from the dropdown menu.
3. **Set Temperature:** Adjust the temperature value as needed.
4. **Add Custom Text:** Enter any custom prefix or suffix text in the provided text boxes.
5. **Process Transcript:** Click "Copy and Get Answer" to send the latest transcript to the selected LLM. The response will be displayed in the output text box.

<img src="gui_en.png" width="400">
