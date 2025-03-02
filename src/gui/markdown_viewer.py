import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from PyQt6.QtWidgets import QApplication
import src.config.config
import re

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
        # 配置代码高亮扩展
        codehilite_extension = CodeHiliteExtension(
            noclasses=False,  # 使用CSS类而非内联样式
            linenums=False,   # 默认不显示行号
            guess_lang=True   # 自动检测语言
        )

        # 将 Markdown 转换为 HTML
        html = markdown.markdown(
            text,
            extensions=[
                'tables', 
                codehilite_extension, 
                FencedCodeExtension(),
                'nl2br'  # 将换行符转换为<br>标签
            ]
        )
        
        # 处理代码语言标签
        html = process_language_tags(html)
        
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

def process_language_tags(html):
    """
    处理代码块的语言标签，增加语言显示
    
    Args:
        html: 已转换的HTML内容
        
    Returns:
        处理后的HTML内容
    """
    # 匹配 <pre><code class="language-xxx"> 模式
    pattern = r'<pre><code class="language-([a-zA-Z0-9_+-]+)">'
    
    def add_language_label(match):
        lang = match.group(1)
        # 如果是常见语言，美化显示名称
        lang_display = {
            'py': 'Python', 'python': 'Python',
            'js': 'JavaScript', 'javascript': 'JavaScript',
            'java': 'Java',
            'cpp': 'C++', 'c++': 'C++',
            'cs': 'C#', 'csharp': 'C#',
            'php': 'PHP',
            'html': 'HTML',
            'css': 'CSS',
            'bash': 'Bash',
            'sql': 'SQL',
            'json': 'JSON',
            'xml': 'XML',
            'md': 'Markdown', 'markdown': 'Markdown',
            'rb': 'Ruby', 'ruby': 'Ruby',
            'go': 'Go',
            'rust': 'Rust',
            'ts': 'TypeScript', 'typescript': 'TypeScript'
        }.get(lang.lower(), lang)
        
        # 返回添加了语言标签的HTML
        return f'<pre><div class="code-header"><span class="code-language">{lang_display}</span></div><code class="language-{lang}">'
    
    return re.sub(pattern, add_language_label, html)

def generate_light_html(html_content):
    """生成带有亮色主题样式的 HTML"""
    theme = src.config.config.THEMES["light"]
    font_family = src.config.config.UI_FONT_FAMILY
    
    return f"""
    <html>
    <head>
    <style>
        body {{ 
            font-family: {font_family};
            color: {theme['text']};
            line-height: 1.6;
        }}
        h1, h2, h3, h4, h5, h6 {{ 
            color: {theme['md_header']};
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        h1 {{ font-size: 24px; }}
        h2 {{ font-size: 20px; }}
        h3 {{ font-size: 18px; }}
        h4 {{ font-size: 16px; }}
        p {{ margin-bottom: 12px; line-height: 1.6; }}
        code {{ 
            background-color: {theme['md_code_bg']};
            padding: 2px 4px;
            border-radius: {src.config.config.UI_BORDER_RADIUS};
            font-family: Consolas, "Courier New", monospace;
        }}
        pre {{ 
            background-color: {theme['md_code_bg']};
            padding: 0;
            border-radius: {src.config.config.UI_BORDER_RADIUS};
            overflow-x: auto;
            margin: 16px 0;
            border: 1px solid #E2E8F0;
        }}
        pre code {{ 
            background-color: transparent; 
            padding: 12px;
            display: block;
            overflow-x: auto;
            font-size: 14px;
            line-height: 1.5;
        }}
        .code-header {{
            background-color: #F8FAFC;
            border-bottom: 1px solid #E2E8F0;
            padding: 6px 12px;
            font-family: {font_family};
            font-size: 12px;
            color: #64748B;
            display: flex;
            justify-content: flex-end;
        }}
        .code-language {{
            display: inline-block;
            font-weight: bold;
        }}
        blockquote {{ 
            border-left: 4px solid {theme['md_blockquote_border']};
            padding-left: 12px;
            color: {theme['md_blockquote']};
            margin: 12px 0;
        }}
        a {{ 
            color: {theme['md_link']};
            text-decoration: none;
        }}
        a:hover {{ text-decoration: underline; }}
        ul, ol {{ padding-left: 20px; margin-bottom: 12px; }}
        li {{ margin-bottom: 4px; }}
        table {{ 
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 12px;
        }}
        th, td {{ 
            border: 1px solid {theme['md_table_border']};
            padding: 8px;
            text-align: left;
        }}
        th {{ background-color: {theme['md_table_header_bg']}; }}
        
        /* Pygments 语法高亮样式 - 亮色主题 */
        .codehilite .hll {{ background-color: #ffffcc }}
        .codehilite .c {{ color: #60a0b0; font-style: italic }}
        .codehilite .err {{ border: 1px solid #FF0000 }}
        .codehilite .k {{ color: #007020; font-weight: bold }}
        .codehilite .o {{ color: #666666 }}
        .codehilite .ch {{ color: #60a0b0; font-style: italic }}
        .codehilite .cm {{ color: #60a0b0; font-style: italic }}
        .codehilite .cp {{ color: #007020 }}
        .codehilite .cpf {{ color: #60a0b0; font-style: italic }}
        .codehilite .c1 {{ color: #60a0b0; font-style: italic }}
        .codehilite .cs {{ color: #60a0b0; background-color: #fff0f0 }}
        .codehilite .gd {{ color: #A00000 }}
        .codehilite .ge {{ font-style: italic }}
        .codehilite .gr {{ color: #FF0000 }}
        .codehilite .gh {{ color: #000080; font-weight: bold }}
        .codehilite .gi {{ color: #00A000 }}
        .codehilite .go {{ color: #888888 }}
        .codehilite .gp {{ color: #c65d09; font-weight: bold }}
        .codehilite .gs {{ font-weight: bold }}
        .codehilite .gu {{ color: #800080; font-weight: bold }}
        .codehilite .gt {{ color: #0044DD }}
        .codehilite .kc {{ color: #007020; font-weight: bold }}
        .codehilite .kd {{ color: #007020; font-weight: bold }}
        .codehilite .kn {{ color: #007020; font-weight: bold }}
        .codehilite .kp {{ color: #007020 }}
        .codehilite .kr {{ color: #007020; font-weight: bold }}
        .codehilite .kt {{ color: #902000 }}
        .codehilite .m {{ color: #40a070 }}
        .codehilite .s {{ color: #4070a0 }}
        .codehilite .na {{ color: #4070a0 }}
        .codehilite .nb {{ color: #007020 }}
        .codehilite .nc {{ color: #0e84b5; font-weight: bold }}
        .codehilite .no {{ color: #60add5 }}
        .codehilite .nd {{ color: #555555; font-weight: bold }}
        .codehilite .ni {{ color: #d55537; font-weight: bold }}
        .codehilite .ne {{ color: #007020 }}
        .codehilite .nf {{ color: #06287e }}
        .codehilite .nl {{ color: #002070; font-weight: bold }}
        .codehilite .nn {{ color: #0e84b5; font-weight: bold }}
        .codehilite .nt {{ color: #062873; font-weight: bold }}
        .codehilite .nv {{ color: #bb60d5 }}
        .codehilite .ow {{ color: #007020; font-weight: bold }}
        .codehilite .w {{ color: #bbbbbb }}
        .codehilite .mb {{ color: #40a070 }}
        .codehilite .mf {{ color: #40a070 }}
        .codehilite .mh {{ color: #40a070 }}
        .codehilite .mi {{ color: #40a070 }}
        .codehilite .mo {{ color: #40a070 }}
        .codehilite .sa {{ color: #4070a0 }}
        .codehilite .sb {{ color: #4070a0 }}
        .codehilite .sc {{ color: #4070a0 }}
        .codehilite .dl {{ color: #4070a0 }}
        .codehilite .sd {{ color: #4070a0; font-style: italic }}
        .codehilite .s2 {{ color: #4070a0 }}
        .codehilite .se {{ color: #4070a0; font-weight: bold }}
        .codehilite .sh {{ color: #4070a0 }}
        .codehilite .si {{ color: #70a0d0; font-style: italic }}
        .codehilite .sx {{ color: #c65d09 }}
        .codehilite .sr {{ color: #235388 }}
        .codehilite .s1 {{ color: #4070a0 }}
        .codehilite .ss {{ color: #517918 }}
        .codehilite .bp {{ color: #007020 }}
        .codehilite .fm {{ color: #06287e }}
        .codehilite .vc {{ color: #bb60d5 }}
        .codehilite .vg {{ color: #bb60d5 }}
        .codehilite .vi {{ color: #bb60d5 }}
        .codehilite .vm {{ color: #bb60d5 }}
        .codehilite .il {{ color: #40a070 }}
    </style>
    </head>
    <body>{html_content}</body>
    </html>
    """

def generate_dark_html(html_content):
    """生成带有暗色主题样式的 HTML"""
    theme = src.config.config.THEMES["dark"]
    font_family = src.config.config.UI_FONT_FAMILY
    
    return f"""
    <html>
    <head>
    <style>
        body {{ 
            font-family: {font_family};
            color: {theme['text']};
            line-height: 1.6;
        }}
        h1, h2, h3, h4, h5, h6 {{ 
            color: {theme['md_header']};
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        h1 {{ font-size: 24px; }}
        h2 {{ font-size: 20px; }}
        h3 {{ font-size: 18px; }}
        h4 {{ font-size: 16px; }}
        p {{ margin-bottom: 12px; line-height: 1.6; }}
        code {{ 
            background-color: {theme['md_code_bg']};
            color: {theme['text']};
            padding: 2px 4px;
            border-radius: {src.config.config.UI_BORDER_RADIUS};
            font-family: Consolas, "Courier New", monospace;
        }}
        pre {{ 
            background-color: {theme['md_code_bg']};
            padding: 0;
            border-radius: {src.config.config.UI_BORDER_RADIUS};
            overflow-x: auto;
            margin: 16px 0;
            border: 1px solid #3E4C5A;
        }}
        pre code {{ 
            background-color: transparent; 
            padding: 12px;
            display: block;
            overflow-x: auto;
            font-size: 14px;
            line-height: 1.5;
        }}
        .code-header {{
            background-color: #1a2234;
            border-bottom: 1px solid #3E4C5A;
            padding: 6px 12px;
            font-family: {font_family};
            font-size: 12px;
            color: #94A3B8;
            display: flex;
            justify-content: flex-end;
        }}
        .code-language {{
            display: inline-block;
            font-weight: bold;
        }}
        blockquote {{ 
            border-left: 4px solid {theme['md_blockquote_border']};
            padding-left: 12px;
            color: {theme['md_blockquote']};
            margin: 12px 0;
        }}
        a {{ 
            color: {theme['md_link']};
            text-decoration: none;
        }}
        a:hover {{ text-decoration: underline; }}
        ul, ol {{ padding-left: 20px; margin-bottom: 12px; }}
        li {{ margin-bottom: 4px; }}
        table {{ 
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 12px;
        }}
        th, td {{ 
            border: 1px solid {theme['md_table_border']};
            padding: 8px;
            text-align: left;
        }}
        th {{ background-color: {theme['md_table_header_bg']}; }}
        
        /* Pygments 语法高亮样式 - 暗色主题 */
        .codehilite .hll {{ background-color: #49483e }}
        .codehilite {{ background: {theme['md_code_bg']}; color: #f8f8f2 }}
        .codehilite .c {{ color: #75715e }}
        .codehilite .err {{ color: #960050; background-color: #1e0010 }}
        .codehilite .k {{ color: #66d9ef }}
        .codehilite .l {{ color: #ae81ff }}
        .codehilite .n {{ color: #f8f8f2 }}
        .codehilite .o {{ color: #f92672 }}
        .codehilite .p {{ color: #f8f8f2 }}
        .codehilite .ch {{ color: #75715e }}
        .codehilite .cm {{ color: #75715e }}
        .codehilite .cp {{ color: #75715e }}
        .codehilite .cpf {{ color: #75715e }}
        .codehilite .c1 {{ color: #75715e }}
        .codehilite .cs {{ color: #75715e }}
        .codehilite .gd {{ color: #f92672 }}
        .codehilite .ge {{ font-style: italic }}
        .codehilite .gi {{ color: #a6e22e }}
        .codehilite .gs {{ font-weight: bold }}
        .codehilite .gu {{ color: #75715e }}
        .codehilite .kc {{ color: #66d9ef }}
        .codehilite .kd {{ color: #66d9ef }}
        .codehilite .kn {{ color: #f92672 }}
        .codehilite .kp {{ color: #66d9ef }}
        .codehilite .kr {{ color: #66d9ef }}
        .codehilite .kt {{ color: #66d9ef }}
        .codehilite .ld {{ color: #e6db74 }}
        .codehilite .m {{ color: #ae81ff }}
        .codehilite .s {{ color: #e6db74 }}
        .codehilite .na {{ color: #a6e22e }}
        .codehilite .nb {{ color: #f8f8f2 }}
        .codehilite .nc {{ color: #a6e22e }}
        .codehilite .no {{ color: #66d9ef }}
        .codehilite .nd {{ color: #a6e22e }}
        .codehilite .ni {{ color: #f8f8f2 }}
        .codehilite .ne {{ color: #a6e22e }}
        .codehilite .nf {{ color: #a6e22e }}
        .codehilite .nl {{ color: #f8f8f2 }}
        .codehilite .nn {{ color: #f8f8f2 }}
        .codehilite .nx {{ color: #a6e22e }}
        .codehilite .py {{ color: #f8f8f2 }}
        .codehilite .nt {{ color: #f92672 }}
        .codehilite .nv {{ color: #f8f8f2 }}
        .codehilite .ow {{ color: #f92672 }}
        .codehilite .w {{ color: #f8f8f2 }}
        .codehilite .mb {{ color: #ae81ff }}
        .codehilite .mf {{ color: #ae81ff }}
        .codehilite .mh {{ color: #ae81ff }}
        .codehilite .mi {{ color: #ae81ff }}
        .codehilite .mo {{ color: #ae81ff }}
        .codehilite .sa {{ color: #e6db74 }}
        .codehilite .sb {{ color: #e6db74 }}
        .codehilite .sc {{ color: #e6db74 }}
        .codehilite .dl {{ color: #e6db74 }}
        .codehilite .sd {{ color: #e6db74 }}
        .codehilite .s2 {{ color: #e6db74 }}
        .codehilite .se {{ color: #ae81ff }}
        .codehilite .sh {{ color: #e6db74 }}
        .codehilite .si {{ color: #e6db74 }}
        .codehilite .sx {{ color: #e6db74 }}
        .codehilite .sr {{ color: #e6db74 }}
        .codehilite .s1 {{ color: #e6db74 }}
        .codehilite .ss {{ color: #e6db74 }}
        .codehilite .bp {{ color: #f8f8f2 }}
        .codehilite .fm {{ color: #a6e22e }}
        .codehilite .vc {{ color: #f8f8f2 }}
        .codehilite .vg {{ color: #f8f8f2 }}
        .codehilite .vi {{ color: #f8f8f2 }}
        .codehilite .vm {{ color: #f8f8f2 }}
        .codehilite .il {{ color: #ae81ff }}
    </style>
    </head>
    <body>{html_content}</body>
    </html>
    """