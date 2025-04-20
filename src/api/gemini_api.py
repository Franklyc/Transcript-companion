import os
import base64
from google import genai
from google.genai import types
import src.config.config

# 辅助函数定义
def get_auxiliary_mode_prompt(mode):
    """
    根据选定的附加模式返回相应的提示词
    
    参数:
    - mode: 附加模式名称
    
    返回:
    - str: 附加模式对应的提示词，如果模式为none则返回空字符串
    """
    if mode == "none":
        return ""
    elif mode == "coding-solution":
        return src.config.config.CODING_SOLUTION_PROMPT
    elif mode == "coding-debug-general":
        return src.config.config.CODING_DEBUG_GENERAL_PROMPT
    elif mode == "coding-debug-correction":
        return src.config.config.CODING_DEBUG_CORRECTION_PROMPT
    elif mode == "coding-debug-time-optimize":
        return src.config.config.CODING_DEBUG_TIME_PROMPT
    elif mode == "coding-debug-space-optimize":
        return src.config.config.CODING_DEBUG_SPACE_PROMPT
    elif mode == "meeting-summarizer":
        return src.config.config.MEETING_SUMMARIZER_PROMPT
    elif mode == "action-item-extractor":
        return src.config.config.ACTION_ITEM_EXTRACTOR_PROMPT
    elif mode == "topic-tracker":
        return src.config.config.TOPIC_TRACKER_PROMPT
    elif mode == "sentiment-analyzer":
        return src.config.config.SENTIMENT_ANALYZER_PROMPT
    elif mode == "question-generator":
        return src.config.config.QUESTION_GENERATOR_PROMPT
    return ""

# encode_image_to_base64 function removed (exists in worker.py)

# fetch_gemini_response function removed (logic moved to worker.py)

# fetch_gemini_response_with_history function removed (logic moved to worker.py)