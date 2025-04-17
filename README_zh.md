# Transcript-companion
[英文版README](README.md)

- [功能](#功能)
- [要求](#要求)
- [核心工作流程](#核心工作流程)
- [设置](#设置)
- [使用方法](#使用方法)
- [界面预览](#界面预览)
  - [浅色主题](#浅色主题)
  - [深色主题](#深色主题)

**一款使用 Python/PyQt6 构建的 GUI 应用程序，它使用 LLM API 处理语音转录本。此工具利用大型语言模型的强大功能，简化了分析和总结会议记录的工作流程。**

## 功能

* **现代化侧边栏界面：** 清新现代的界面设计，配备便捷的侧边栏快速访问常用功能：
    * 语言切换 (🀄/🔤)
    * 主题切换 (🌙/☀️)
    * 帮助文档 (❓)
    * 设置选项 (⚙️)
    * 快速清除 (🗑️)
    * 刷新模型 (🔄)
* **文件夹选择：** 选择包含语音转录文件的目录（例如，`.txt`、`.md`）。
* **多 LLM 支持：** 与各种 LLM 提供商无缝集成：
    * **Cerebras** (llama3.1-70b, llama3.1-8b) :sparkles: **最快：** 快速响应时间的最佳选择
    * **Groq** (mixtral-8x7b-32768, llama-3.1 等模型)
    * **Google Gemini** (gemini-2/2.5 系列模型) :books: **最大上下文：** 长转录的理想选择
    * **Sambanova** (llama-3.1 等模型，包括 llama3.1-405B)
    * **智谱清言** (glm-4-flash 模型)
    * **GLHF** (Llama-3.3-70B 系列模型)
    * **硅基流动** (Qwen2.5-7b 模型)
    * **本地：** (LMstudio/Kobold/Ollama) :computer: **私密：** 数据安全的最佳选择
* **温度控制：** 调整温度参数 (0.0-1.5) 以微调 LLM 响应的创造性和随机性。较低的值会导致更集中和确定的输出，而较高的值会鼓励更多样化和意想不到的生成。
* **可自定义的前缀/后缀：** 在将转录发送到 LLM 之前，向其添加自定义前缀和后缀文本。这允许您向模型提供额外的上下文或说明，从而调整其输出以更好地满足您的需求。
* **图像集成：** 通过视觉内容增强您的提示：
    * **截图和OCR功能：** 捕获屏幕区域并自动从中提取文本
    * **图像上传：** 添加来自本地文件的图片
    * **直接截图：** 捕获屏幕区域而不进行OCR处理
    * **图像预览：** 在应用程序内查看当前选择的图像
    * **视觉模型支持：** 使用兼容的模型同时分析文本和图像
* **Gemini模型增强功能：**
    * **Google搜索集成：** 为Gemini模型启用Google搜索功能，获取最新信息
    * **思考预算控制：** 为gemini-2.5-flash-preview-04-17模型设置思考预算(0-24576)，优化模型在复杂任务上的思考过程和回答质量
* **实时流式传输：** 在生成 LLM 响应时实时查看它们，提供即时反馈以及与模型的动态交互。
* **剪贴板集成：** 轻松将处理后的转录内容复制到剪贴板以在其他应用程序中使用。
* **双语支持（中文/英文）：** GUI 现在支持中文和英文。您可以在应用程序内切换语言。
* **深色模式：** 在浅色和深色主题之间切换，以适应不同的照明条件。使用侧边栏内的月亮/太阳图标切换主题。
* **对话导出：** 将包含提示和回答的对话内容导出为带时间戳的文本文件，保存在 history 文件夹中以供未来回顾。

## 核心工作流程
```mermaid
flowchart TD
    %% 使用更正式的样式
    classDef process fill:#f5f5f5,stroke:#333,stroke-width:1px,color:black,font-family:Arial;
    classDef decision fill:white,stroke:#333,stroke-width:1px,color:black,font-family:Arial,font-size:11px;
    classDef start fill:white,stroke:#333,stroke-width:1.5px,color:black,font-family:Arial;
    
    %% 开始节点和初始化
    Start([系统初始化]) --> MainWindow[初始化应用程序窗口]
    MainWindow --> UI[配置用户界面组件]
    
    subgraph InputPhase["输入获取阶段"]
        style InputPhase fill:#f9f9f9,stroke:#999,stroke-width:1px,stroke-dasharray: 5 5
        
        UI --> SelectFolder[选择源转录目录]
        UI --> ConfigLLM[配置语言模型参数]
        ConfigLLM --> SelectProvider[提供商选择]
        ConfigLLM --> SelectModel[模型指定]
        ConfigLLM --> SetTemperature[温度参数设置]
        
        UI --> InputMethods{输入方式选择}
        InputMethods -->|基于文本| CustomText[文本修改（前缀/后缀）]
        InputMethods -->|基于图像| ImageInput[图像输入处理]
        
        ImageInput --> CaptureOptions{图像获取方式}
        CaptureOptions -->|截图并OCR| OCRProcess[光学字符识别]
        CaptureOptions -->|文件上传| UploadProcess[图像文件处理]
        CaptureOptions -->|屏幕区域截图| ScreenshotProcess[屏幕区域获取]
        
        SelectFolder --> GetTranscript[获取最新转录数据]
        CustomText --> CombineInput[输入数据整合]
        OCRProcess --> CombineInput
        UploadProcess --> CombineInput
        ScreenshotProcess --> CombineInput
        GetTranscript --> CombineInput
    end
    
    subgraph ModelPhase["模型交互阶段"]
        style ModelPhase fill:#f9f9f9,stroke:#999,stroke-width:1px,stroke-dasharray: 5 5
        
        CombineInput --> APIRequest[API请求形成]
        SelectProvider -.-> APIRequest
        SelectModel -.-> APIRequest
        SetTemperature -.-> APIRequest
        APIRequest --> StreamResponse[响应流处理]
    end
    
    subgraph OutputPhase["输出处理阶段"]
        style OutputPhase fill:#f9f9f9,stroke:#999,stroke-width:1px,stroke-dasharray: 5 5
        
        StreamResponse --> FormatOutput{输出格式确定}
        FormatOutput -->|Markdown内容| RenderMarkdown[Markdown渲染]
        FormatOutput -->|纯文本内容| DisplayText[文本显示]
        
        RenderMarkdown --> ExportOption[导出功能]
        DisplayText --> ExportOption
        ExportOption --> SaveConversation[对话持久化]
    end
    
    SaveConversation --> NewQuery[查询重新初始化]
    NewQuery --> InputMethods
    
    %% 应用样式类到节点
    class Start,MainWindow,UI start;
    class SelectFolder,ConfigLLM,SelectProvider,SelectModel,SetTemperature,CustomText,ImageInput,OCRProcess,UploadProcess,ScreenshotProcess,GetTranscript,CombineInput,APIRequest,StreamResponse,RenderMarkdown,DisplayText,ExportOption,SaveConversation,NewQuery process;
    class InputMethods,CaptureOptions,FormatOutput decision;
```

## 要求

* **Python 3.x**
* **PyQt6**
* 以下 Python 包：
    * ``PyQt6``
    * ``openai``
    * ``pyperclip``
    * ``requests``
    * ``Pillow``
    * ``textract``

您可以使用 pip 安装依赖：

```bash
pip install -r requirements.txt
```

## 设置

1. **克隆存储库：**

   ```bash
   git clone https://github.com/Franklyc/Transcript-companion.git
   ```

2. **配置：**

   * **重命名示例文件：** 复制并重命名以下文件：
      * `config.py.example` 为 `config.py`
      * `prefix.py.example` 为 `prefix.py`
   * **API 密钥：** 打开新创建的 `config.py` 并将占位符 API 密钥替换为您每个 LLM 提供商的实际密钥。这些密钥通常从相应提供商的网站获取。
   * **默认文件夹：** 您还可以修改 `config.py` 中的 `DEFAULT_FOLDER_PATH` 以指向存储转录的目录。
   * **自定义前缀：** 编辑 `prefix.py` 以修改 `get_original_prefix()` 函数。这允许您定义在处理每个转录之前提供给 LLM 的初始说明或上下文。提供清晰简洁的说明以指导 LLM 的响应。

3. **运行应用程序：**

   ```bash
   python main.py
   ```

## 使用方法

1. **了解界面：**
    * 使用侧边栏按钮快速访问常用功能
    * 语言切换按钮 (🀄/🔤) 在中英文之间切换
    * 主题切换按钮 (🌙/☀️) 在浅色和深色主题之间切换
    * 帮助按钮 (❓) 显示使用说明
    * 设置按钮 (⚙️) 用于额外选项
    * 清除按钮 (🗑️) 快速清空所有输入输出区域
    * 刷新按钮 (🔄) 更新可用的本地模型列表
2. **选择文件夹：** 单击"选择文件夹"并导航到包含转录文件的目录。
3. **选择模型：** 从下拉菜单中选择所需的 LLM 模型。
4. **设置温度：** 根据需要调整温度值。
5. **添加自定义文本：** 在提供的文本框中输入任何自定义前缀或后缀文本。
6. **添加图像或截图：**
    * 点击"截图并OCR"捕获屏幕区域并从中提取文本
    * 点击"上传图片"从您的计算机中选择图像
    * 点击"截图"获取屏幕截图而不进行OCR处理
    * 使用图像预览区域查看当前选择的图像
    * 点击"清除图片"移除当前图像
7. **处理转录：** 单击"复制并获取回答"以将最新的转录发送到所选的 LLM。响应将显示在输出文本框中。
8. **导出对话：** 点击"导出对话"按钮将提示和回答保存到 history 文件夹中的带时间戳的文件中。

## 界面预览

### 浅色主题
<img src="assets\ZH\UI_light_1_zh.png" width="400">
<img src="assets\ZH\UI_light_2_zh.png" width="400">

### 深色主题
<img src="assets\ZH\UI_dark_1_zh.png" width="400">
<img src="assets\ZH\UI_dark_2_zh.png" width="400">
