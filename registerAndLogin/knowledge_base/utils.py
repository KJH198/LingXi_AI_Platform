import os
import markdown
from docx import Document
import mammoth

def get_file_extension(filename):
    """获取文件扩展名(小写)"""
    return os.path.splitext(filename)[1].lower()

def process_text_file(file_path):
    """处理文本文件，返回内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # 尝试使用 latin-1 编码
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.read()

def process_markdown_file(file_path):
    """处理Markdown文件，返回HTML内容"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        md_content = f.read()
        html_content = markdown.markdown(
            md_content, 
            extensions=['extra', 'codehilite', 'tables']
        )
        return html_content, md_content

def process_docx_file(file_path):
    """处理DOCX文件，返回HTML和文本内容"""
    # 使用mammoth转换为HTML
    with open(file_path, 'rb') as docx_file:
        result = mammoth.convert_to_html(docx_file)
        html_content = result.value
        
        # 提取纯文本内容
        doc = Document(file_path)
        text_content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        
        return html_content, text_content