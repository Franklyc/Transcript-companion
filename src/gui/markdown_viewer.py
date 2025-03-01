import markdown
from PyQt6.QtWidgets import QApplication

def render_markdown(text_browser, text, is_dark_theme=False):
    """
    将 Markdown 文本渲染为 HTML 并显示在 QTextBrowser 中
    
    Args:
        text_browser: QTextBrowser 实例
        text: Markdown 格式的文本
        is_dark_theme: 是否使用暗色主题
    """
    if not text:
        return
        
    try:
        # 将 Markdown 转换为 HTML
        html = markdown.markdown(
            text,
            extensions=['tables', 'fenced_code', 'codehilite']
        )
        
        # 根据主题选择适当的样式
        if is_dark_theme:
            styled_html = generate_dark_html(html)
        else:
            styled_html = generate_light_html(html)
        
        # 设置 HTML 内容
        text_browser.setHtml(styled_html)
        
        # 处理 Qt 事件循环，确保 UI 及时更新
        QApplication.processEvents()
    except Exception as e:
        text_browser.setPlainText(f"Markdown 渲染错误: {str(e)}\n\n{text}")

def append_markdown_text(text_browser, current_text, new_text, is_markdown_mode, is_dark_theme=False):
    """
    追加文本到输出区域，根据模式决定是否渲染为 Markdown
    
    Args:
        text_browser: QTextBrowser 实例
        current_text: 当前已有的原始文本
        new_text: 要追加的新文本
        is_markdown_mode: 是否启用 Markdown 模式
        is_dark_theme: 是否使用暗色主题
    
    Returns:
        updated_text: 更新后的原始文本
    """
    updated_text = current_text + new_text
    
    if is_markdown_mode:
        # 更新 Markdown 渲染
        render_markdown(text_browser, updated_text, is_dark_theme)
    else:
        # 直接显示文本
        text_browser.setPlainText(updated_text)
    
    # 滚动到底部
    sb = text_browser.verticalScrollBar()
    sb.setValue(sb.maximum())
    
    # 处理 Qt 事件循环，确保 UI 及时更新
    QApplication.processEvents()
    
    return updated_text

def generate_light_html(html_content):
    """生成带有亮色主题样式的 HTML"""
    return f"""
    <html>
    <head>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; }}
        h1, h2, h3, h4, h5, h6 {{ color: #3B82F6; margin-top: 20px; margin-bottom: 10px; }}
        h1 {{ font-size: 24px; }}
        h2 {{ font-size: 20px; }}
        h3 {{ font-size: 18px; }}
        h4 {{ font-size: 16px; }}
        p {{ margin-bottom: 12px; line-height: 1.6; }}
        code {{ background-color: #F1F5F9; padding: 2px 4px; border-radius: 3px; font-family: Consolas, monospace; }}
        pre {{ background-color: #F1F5F9; padding: 12px; border-radius: 5px; overflow-x: auto; }}
        pre code {{ background-color: transparent; padding: 0; }}
        blockquote {{ border-left: 4px solid #CBD5E1; padding-left: 12px; color: #64748B; margin: 12px 0; }}
        a {{ color: #3B82F6; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        ul, ol {{ padding-left: 20px; margin-bottom: 12px; }}
        li {{ margin-bottom: 4px; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 12px; }}
        th, td {{ border: 1px solid #E2E8F0; padding: 8px; text-align: left; }}
        th {{ background-color: #F1F5F9; }}
    </style>
    </head>
    <body>{html_content}</body>
    </html>
    """

def generate_dark_html(html_content):
    """生成带有暗色主题样式的 HTML"""
    return f"""
    <html>
    <head>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #E2E8F0; }}
        h1, h2, h3, h4, h5, h6 {{ color: #3B82F6; margin-top: 20px; margin-bottom: 10px; }}
        h1 {{ font-size: 24px; }}
        h2 {{ font-size: 20px; }}
        h3 {{ font-size: 18px; }}
        h4 {{ font-size: 16px; }}
        p {{ margin-bottom: 12px; line-height: 1.6; }}
        code {{ background-color: #1E293B; color: #E2E8F0; padding: 2px 4px; border-radius: 3px; font-family: Consolas, monospace; }}
        pre {{ background-color: #1E293B; padding: 12px; border-radius: 5px; overflow-x: auto; }}
        pre code {{ background-color: transparent; padding: 0; }}
        blockquote {{ border-left: 4px solid #4B5563; padding-left: 12px; color: #94A3B8; margin: 12px 0; }}
        a {{ color: #60A5FA; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        ul, ol {{ padding-left: 20px; margin-bottom: 12px; }}
        li {{ margin-bottom: 4px; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 12px; }}
        th, td {{ border: 1px solid #4B5563; padding: 8px; text-align: left; }}
        th {{ background-color: #1E293B; }}
    </style>
    </head>
    <body>{html_content}</body>
    </html>
    """