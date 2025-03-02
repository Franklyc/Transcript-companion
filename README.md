# Transcript-companion
[中文版README](README_zh.md)

- [Features](#features)
- [Requirements](#requirements)
- [Setup](#setup)
- [Usage](#usage)
- [Interface Preview](#interface-preview)
  - [Light Theme](#light-theme)
  - [Dark Theme](#dark-theme)

**A GUI application built with Python/PyQt6 that processes speech transcripts using LLM APIs. This tool simplifies the workflow of analyzing and summarizing meeting recordings by leveraging the power of large language models.**

## Features

* **Modern UI with Sidebar:** A clean, modern interface with a convenient sidebar for quick access to common functions:
    * Language Toggle (🀄/🔤)
    * Theme Toggle (🌙/☀️)
    * Help (❓)
    * Settings (⚙️)
    * Quick Clear (🗑️)
    * Refresh Models (🔄)
* **Folder Selection:** Choose the directory containing your speech transcription files (e.g., `.txt`, `.md`).
* **Multi-LLM Support:** Seamlessly integrate with various LLM providers:
    * **Cerebras** (llama3.1-70b, llama3.1-8b) :sparkles: **FASTEST:** Best choice for quick response times
    * **Groq** (mixtral-8x7b-32768, llama-3.1/3.3 models) 
    * **Google Gemini** (gemini-1.5-flash models) :books: **LARGEST CONTEXT:** Ideal for long transcripts
    * **Sambanova** (llama-3.1 models, including llama3.1-405B, Qwen2.5 models)
    * **Zhipu** (glm-4-flash)
    * **GLHF** (Llama-3.3-70B)
    * **SiliconFlow** (Qwen2.5-7b)
    * **LOCAL** (LMstudio/Kobold/Ollama) :computer: **PRIVATE:** Best choice for data security
* **Temperature Control:** Adjust the temperature parameter (0.0-1.5) to fine-tune the creativity and randomness of the LLM's responses. Lower values result in more focused and deterministic outputs, while higher values encourage more diverse and unexpected generation.
* **Customizable Prefix/Suffix:** Add custom prefix and suffix text to your transcripts before sending them to the LLM. This allows you to provide additional context or instructions to the model, shaping its output to better suit your needs.
* **Image Integration:** Enhance your prompts with visual content:
    * **Screenshot with OCR:** Capture a region of your screen and automatically extract text from it
    * **Image Upload:** Add images from your local files
    * **Direct Screenshot:** Capture a region of your screen without OCR processing
    * **Image Preview:** View the currently selected image within the application
    * **Vision Models Support:** Use compatible models to analyze both text and images together
* **Real-time Streaming:** View LLM responses in real-time as they are generated, providing immediate feedback and a dynamic interaction with the model.
* **Clipboard Integration:** Easily copy the processed transcript content to the clipboard for use in other applications.
* **Bilingual Support (Chinese/English):** The GUI now supports both Chinese and English. You can switch between languages within the application.
* **Dark Mode:** Toggle between light and dark themes for comfortable viewing in different lighting conditions. Use the moon/sun icon in the sidebar to switch themes.
* **Conversation Export:** Export conversations including prompts and responses to timestamped text files in the history folder for future reference.

## Core workflow
```mermaid
flowchart TD
    %% Use more formal styling
    classDef process fill:#f5f5f5,stroke:#333,stroke-width:1px,color:black,font-family:Arial;
    classDef decision fill:white,stroke:#333,stroke-width:1px,color:black,font-family:Arial,font-size:11px;
    classDef start fill:white,stroke:#333,stroke-width:1.5px,color:black,font-family:Arial;
    
    %% Start node and initialization
    Start([System Initialization]) --> MainWindow[Initialize Application Window]
    MainWindow --> UI[Configure User Interface Components]
    
    subgraph InputPhase["Input Acquisition Phase"]
        style InputPhase fill:#f9f9f9,stroke:#999,stroke-width:1px,stroke-dasharray: 5 5
        
        UI --> SelectFolder[Select Source Transcript Directory]
        UI --> ConfigLLM[Configure Language Model Parameters]
        ConfigLLM --> SelectProvider[Provider Selection]
        ConfigLLM --> SelectModel[Model Specification]
        ConfigLLM --> SetTemperature[Temperature Parameter Setting]
        
        UI --> InputMethods{Input Modality Selection}
        InputMethods -->|Text-Based| CustomText[Text Modification with Prefix/Suffix]
        InputMethods -->|Image-Based| ImageInput[Image Input Processing]
        
        ImageInput --> CaptureOptions{Image Acquisition Method}
        CaptureOptions -->|Screen Capture with OCR| OCRProcess[Optical Character Recognition]
        CaptureOptions -->|File Upload| UploadProcess[Image File Processing]
        CaptureOptions -->|Screen Region Capture| ScreenshotProcess[Screen Region Acquisition]
        
        SelectFolder --> GetTranscript[Retrieve Latest Transcript Data]
        CustomText --> CombineInput[Input Data Integration]
        OCRProcess --> CombineInput
        UploadProcess --> CombineInput
        ScreenshotProcess --> CombineInput
        GetTranscript --> CombineInput
    end
    
    subgraph ModelPhase["Model Interaction Phase"]
        style ModelPhase fill:#f9f9f9,stroke:#999,stroke-width:1px,stroke-dasharray: 5 5
        
        CombineInput --> APIRequest[API Request Formation]
        SelectProvider -.-> APIRequest
        SelectModel -.-> APIRequest
        SetTemperature -.-> APIRequest
        APIRequest --> StreamResponse[Response Stream Processing]
    end
    
    subgraph OutputPhase["Output Processing Phase"]
        style OutputPhase fill:#f9f9f9,stroke:#999,stroke-width:1px,stroke-dasharray: 5 5
        
        StreamResponse --> FormatOutput{Output Format Determination}
        FormatOutput -->|Markdown Content| RenderMarkdown[Markdown Rendering]
        FormatOutput -->|Plain Text Content| DisplayText[Text Display]
        
        RenderMarkdown --> ExportOption[Export Functionality]
        DisplayText --> ExportOption
        ExportOption --> SaveConversation[Conversation Persistence]
    end
    
    SaveConversation --> NewQuery[Query Reinitiation]
    NewQuery --> InputMethods
    
    %% Apply classes to nodes
    class Start,MainWindow,UI start;
    class SelectFolder,ConfigLLM,SelectProvider,SelectModel,SetTemperature,CustomText,ImageInput,OCRProcess,UploadProcess,ScreenshotProcess,GetTranscript,CombineInput,APIRequest,StreamResponse,RenderMarkdown,DisplayText,ExportOption,SaveConversation,NewQuery process;
    class InputMethods,CaptureOptions,FormatOutput decision;
```

## Requirements

* **Python 3.x**
* **PyQt6**
* The following Python packages:
    * ``PyQt6``
    * ``openai``
    * ``pyperclip``
    * ``requests``
    * ``Pillow``
    * ``textract``

You can install these packages using pip:

```bash
pip install -r requirements.txt
```

## Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Franklyc/Transcript-companion.git
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

1. **Understand the Interface:**
    * Use the sidebar buttons for quick access to common functions
    * Language toggle (🀄/🔤) switches between Chinese and English
    * Theme toggle (🌙/☀️) switches between light and dark modes
    * Help button (❓) shows usage instructions
    * Settings button (⚙️) for additional options
    * Clear button (🗑️) quickly clears all input/output fields
    * Refresh button (🔄) updates the list of available local models
2. **Select Folder:** Click "Select Folder" and navigate to the directory containing your transcript files.
3. **Choose Model:** Select your desired LLM model from the dropdown menu.
4. **Set Temperature:** Adjust the temperature value as needed.
5. **Add Custom Text:** Enter any custom prefix or suffix text in the provided text boxes.
6. **Add Images or Screenshots:**
    * Click "Screenshot and OCR" to capture a screen region and extract text from it
    * Click "Upload Image" to select an image from your computer
    * Click "Capture Screenshot" to take a screenshot without OCR
    * Use the image preview area to see your currently selected image
    * Click "Clear Image" to remove the current image
7. **Process Transcript:** Click "Copy and Get Answer" to send the latest transcript to the selected LLM. The response will be displayed in the output text box.
8. **Export Conversation:** Click the "Export Conversation" button to save both the prompt and response to a timestamped file in the history folder.

## Interface Preview

### Light Theme
<img src="assets\EN\UI_light_1_en.png" width="400">
<img src="assets\EN\UI_light_2_en.png" width="400">

### Dark Theme
<img src="assets\EN\UI_dark_1_en.png" width="400">
<img src="assets\EN\UI_dark_2_en.png" width="400">
