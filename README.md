# TMSpeech-companion

A GUI application built with Python/Tkinter that processes speech transcripts using LLM APIs.

## Features

- Select folder containing speech transcription files
- Support for multiple LLM providers:
  - Cerebras (llama3.1-70b, llama3.1-8b)
  - Groq (mixtral-8x7b-32768, llama-3.1 models) 
  - Google Gemini (gemini-1.5-flash models)
- Customizable temperature parameter (0.0-1.5)
- Custom prefix/suffix text support
- Real-time streaming responses
- Copy transcript content to clipboard

## Requirements

- Python 3.x
- Required packages:
  - tkinter
  - openai
  - pyperclip

## Setup

1. Clone this repository
2. Install dependencies
3. Set up API keys as environment variables:
   - `CEREBRAS_API_KEY`
   - `GROQ_API_KEY` 
   - `GEMINI_API_KEY`
4. Run `python main.py`

## Usage

1. Select the folder containing transcription files
2. Choose an LLM model from the dropdown
3. Adjust temperature value if needed
4. Add any custom prefix/suffix text
5. Click "复制并获取回答" to process the latest transcript

The application will display the LLM response in real-time in the output text box.