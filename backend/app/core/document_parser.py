"""多格式文档解析器"""
import os
from pathlib import Path


def parse_document(file_path: str) -> str:
    """根据文件类型解析文档内容"""
    ext = Path(file_path).suffix.lower()
    parsers = {
        '.pdf': parse_pdf,
        '.docx': parse_docx,
        '.doc': parse_docx,
        '.md': parse_markdown,
        '.txt': parse_text,
        '.html': parse_html,
        '.htm': parse_html,
    }
    parser = parsers.get(ext)
    if not parser:
        raise ValueError(f"不支持的文件格式: {ext}")
    return parser(file_path)


def parse_pdf(file_path: str) -> str:
    """解析 PDF 文件"""
    from pypdf import PdfReader
    reader = PdfReader(file_path)
    text_parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_parts.append(text)
    return '\n\n'.join(text_parts)


def parse_docx(file_path: str) -> str:
    """解析 Word 文档"""
    from docx import Document
    doc = Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return '\n\n'.join(paragraphs)


def parse_markdown(file_path: str) -> str:
    """解析 Markdown 文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def parse_text(file_path: str) -> str:
    """解析纯文本文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def parse_html(file_path: str) -> str:
    """解析 HTML 文件"""
    from bs4 import BeautifulSoup
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    return soup.get_text(separator='\n', strip=True)
