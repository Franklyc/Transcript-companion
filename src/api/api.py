import openai
import base64
import json
from src.config.config import get_provider_info
# from PyQt6.QtWidgets import QApplication # No longer needed here
from src.gui.lang import STRINGS
import src.config.config
from src.api.gemini_api import get_auxiliary_mode_prompt # Keep only this import
# Note: Gemini functions might need refactoring later if they are blocking


def _get_openai_client(model_name):
    provider_info = get_provider_info(model_name)
    if (provider_info):
        client = openai.OpenAI(
            base_url=provider_info.base_url,
            api_key=provider_info.api_key
        )
        clean_model_name = model_name[model_name.index("]") + 2:]
        return client, clean_model_name
    return openai.OpenAI(), model_name

def encode_image_to_base64(image_path):
    """Encode an image file to base64 string"""
    if not image_path:
        return None
        
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# fetch_model_response and fetch_model_response_with_history functions are removed
# as their logic is now handled by ApiWorker in worker.py
