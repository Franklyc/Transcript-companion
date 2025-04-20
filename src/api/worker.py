# src/api/worker.py
import time
import os # Needed for Gemini API Key
from PyQt6.QtCore import QObject, pyqtSignal
import openai
from google import genai # Import google genai
from google.genai import types # Import google genai types

# Helper functions and imports from config/lang
from src.config.config import get_provider_info
import src.config.config
from src.gui.lang import STRINGS
from src.api.gemini_api import get_auxiliary_mode_prompt # Keep this helper
import base64

# Helper function (can be moved from api.py or kept there and imported)
def _get_openai_client(model_name):
    provider_info = get_provider_info(model_name)
    if (provider_info):
        client = openai.OpenAI(
            base_url=provider_info.base_url,
            api_key=provider_info.api_key
        )
        clean_model_name = model_name[model_name.index("]") + 2:]
        return client, clean_model_name
    # Fallback or handle error if provider info not found
    # For simplicity, returning default client, but might need better error handling
    print(f"Warning: Provider info not found for {model_name}. Using default OpenAI client.")
    return openai.OpenAI(), model_name # Or raise an error

def encode_image_to_base64(image_path):
    """Encode an image file to base64 string"""
    if not image_path:
        return None
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        return None

class ApiWorker(QObject):
    """处理 API 请求的后台工作线程"""
    new_chunk_received = pyqtSignal(str)  # 信号：收到新的文本块
    request_finished = pyqtSignal(str)  # 信号：请求完成，传递完整响应
    request_error = pyqtSignal(str)     # 信号：请求出错

    def __init__(self, model_name, temperature, prompt, history=None, image_paths=None, use_history=False):
        super().__init__()
        self.model_name = model_name
        self.temperature = temperature
        self.prompt = prompt
        self.history = history if history is not None else []
        self.image_paths = image_paths
        self.use_history = use_history
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run_request(self):
        """执行 API 请求并处理流式响应"""
        try:
            # --- 重构自 fetch_model_response / fetch_model_response_with_history ---

            # 检查是否启用了附加模式
            aux_mode = src.config.config.CURRENT_AUXILIARY_MODE
            aux_prompt = get_auxiliary_mode_prompt(aux_mode)

            # 如果启用了附加模式，将附加提示词添加到prompt后面
            if aux_prompt and self.prompt:
                final_prompt = f"{self.prompt}\n\n{aux_prompt}"
            else:
                final_prompt = self.prompt

            # 检查是否为Gemini模型
            if "[Gemini]" in self.model_name:
                # --- Gemini API Logic ---
                print("Using Gemini API via Worker")
                client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
                clean_model_name = self.model_name[self.model_name.index("]") + 2:]

                # --- Build Contents (History + Current Prompt + Images) ---
                contents = []
                system_instruction_text = "你是一个专业的助手，分析会议或对话记录" # Default system instruction

                # Handle history
                if self.use_history:
                    for role, content in self.history:
                        if role == "system":
                             # System instruction is handled separately in config
                             # system_instruction_text = content # Optionally override default
                             continue
                        gemini_role = "user" if role == "user" else "model"
                        parts = [types.Part.from_text(text=content)]
                        contents.append(types.Content(role=gemini_role, parts=parts))

                # Handle current user input (text + images)
                user_parts = []
                # Add text part
                if final_prompt:
                     # Apply search command prefix if needed
                     use_search = src.config.config.ENABLE_GEMINI_SEARCH
                     search_reminder_text = "注意：搜索工具已启用，必须结合搜索获取的最新信息来回答。"
                     search_command_prefix = "请务必使用 Google 搜索工具查找最新信息来回答以下问题：\n\n"
                     if use_search:
                         prompt_to_send = search_command_prefix + final_prompt
                         # Optional reminder suffix
                         # prompt_to_send += f"\n\n{search_reminder_text}"
                         # Add search reminder to system instruction as well
                         if search_reminder_text not in system_instruction_text:
                              system_instruction_text += f"\n{search_reminder_text}"
                     else:
                         prompt_to_send = final_prompt
                     user_parts.append(types.Part.from_text(text=prompt_to_send))

                # Add image parts (uploading within worker)
                if self.image_paths and isinstance(self.image_paths, list):
                    print(f"Uploading {len(self.image_paths)} images for Gemini...")
                    for img_path in self.image_paths:
                        if not self._is_running: break # Check stop flag during uploads
                        if os.path.exists(img_path):
                            try:
                                uploaded_file = client.files.upload(file=img_path)
                                image_part = types.Part.from_uri(
                                    file_uri=uploaded_file.uri,
                                    mime_type=uploaded_file.mime_type
                                )
                                user_parts.append(image_part)
                                print(f"Uploaded {img_path} as {uploaded_file.uri}")
                            except Exception as img_upload_err:
                                print(f"Error uploading image {img_path} for Gemini: {img_upload_err}")
                                # Optionally emit an error or warning signal here
                        else:
                             print(f"Image path not found: {img_path}")
                    if not self._is_running: return # Exit if stopped during uploads

                # Append current user message if parts exist
                if user_parts:
                    contents.append(types.Content(role="user", parts=user_parts))

                # --- Configure Request ---
                generate_content_config = types.GenerateContentConfig(
                    temperature=float(self.temperature),
                    top_p=0.95, # Default or make configurable
                    top_k=40,   # Default or make configurable
                    max_output_tokens=8192, # Default or make configurable
                    response_mime_type="text/plain",
                    system_instruction=[types.Part.from_text(text=system_instruction_text)],
                )

                # Add thinking budget if applicable
                if clean_model_name == "gemini-2.5-flash-preview-04-17" and src.config.config.GEMINI_THINKING_BUDGET >= 0:
                    generate_content_config.thinking_config = types.ThinkingConfig(
                        thinking_budget=src.config.config.GEMINI_THINKING_BUDGET
                    )

                # Add search tool if enabled
                if use_search:
                    generate_content_config.tools = [types.Tool(google_search=types.GoogleSearch())]

                # --- Call API and Process Stream ---
                response_stream = client.models.generate_content_stream(
                    model=clean_model_name,
                    contents=contents,
                    config=generate_content_config,
                )

                full_response = ""
                for chunk in response_stream:
                    if not self._is_running:
                        print("Stopping Gemini stream...")
                        # Attempt to cancel the stream if possible (library might not support direct cancellation)
                        break
                    if hasattr(chunk, 'text'):
                        delta = chunk.text or ""
                        full_response += delta
                        self.new_chunk_received.emit(delta) # Emit signal

                if self._is_running:
                    self.request_finished.emit(full_response) # Emit finish signal

                return # Exit after handling Gemini

            # --- OpenAI & Compatible API Logic (remains the same) ---
            messages = []

            if self.use_history:
                # 构建历史消息
                if not self.history or self.history[0][0] != "system":
                     messages.append({"role": "system", "content": "You are a helpful assistant analyzing transcripts from meetings or conversations."})
                for role, content in self.history:
                    if role in ["system", "user", "assistant"]:
                        messages.append({"role": role, "content": content})
            else:
                # 非历史模式，可能需要一个默认的 system prompt
                 messages.append({"role": "system", "content": ""}) # Or a more specific default

            # 添加当前用户消息（支持图像）
            if final_prompt or self.image_paths: # Ensure message is added even if only image exists
                user_message = {"role": "user", "content": []}
                has_image = False

                # Add text content
                if final_prompt:
                    user_message["content"].append({
                        "type": "text",
                        "text": final_prompt
                    })

                # Add image content if provided and model supports vision
                if self.image_paths and any(vision_model in self.model_name for vision_model in ["vision", "VL", "gemini", "claude", "gpt-4"]):
                    image_paths_list = self.image_paths if isinstance(self.image_paths, list) else [self.image_paths]
                    for img_path in image_paths_list:
                        base64_image = encode_image_to_base64(img_path)
                        if base64_image:
                            user_message["content"].append({
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            })
                            has_image = True

                # If no vision capabilities needed or used, revert to simpler format if only text exists
                if not has_image and len(user_message["content"]) == 1 and user_message["content"][0]["type"] == "text":
                     user_message = {"role": "user", "content": final_prompt} # Use simple string content

                messages.append(user_message)


            params = {
                "messages": messages,
                "stream": True,
                "temperature": float(self.temperature),
                "top_p": 1
            }

            client, clean_model_name = _get_openai_client(self.model_name)
            params["model"] = clean_model_name

            # Special handling for specific providers
            if clean_model_name.startswith("cerebras"):
                params["max_completion_tokens"] = 8192 # Example specific param

            stream = client.chat.completions.create(**params)

            full_response = ""
            for chunk in stream:
                if not self._is_running:
                    print("Stopping API stream...")
                    break # Exit loop if stop requested
                delta = chunk.choices[0].delta.content or ""
                full_response += delta
                self.new_chunk_received.emit(delta) # 发出信号传递数据块

            if self._is_running:
                self.request_finished.emit(full_response) # 请求正常完成

        except Exception as e:
            # 获取当前语言设置可能比较困难，暂时硬编码或简化错误信息
            error_message = f"Error during API call: {str(e)}"
            print(f"API Worker Error: {error_message}") # Log error
            if self._is_running: # Only emit error if not intentionally stopped
                 self.request_error.emit(error_message) # 发出错误信号
        finally:
            self._is_running = False # Ensure flag is reset