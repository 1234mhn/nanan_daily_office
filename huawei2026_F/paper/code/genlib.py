# -*- coding: utf-8 -*-
"""F题论文 Word 生成器 —— 第二十三届华为杯官方格式
格式：论文题目三号黑体居中 / 一级标题四号黑体居中 / 其他小四宋体 / 单倍行距 / 无页眉
"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(BASE, "..", "figures")
OUT = os.path.join(BASE, "..", "docx", "F题_论文_前半部分.docx")

HEI = "黑体"
SONG = "宋体"
TIMES = "Times New Roman"

# ---------- 底层工具 ----------
def set_run_font(run, cn=SONG, en=TIMES, size=12, bold=False, color=None):
    run.font.name = en
    run._element.rPr.rFonts.set(qn('w:eastAsia'), cn)
    run.font.size = Pt(size)
    run.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)

def para(doc, text="", size=12, cn=SONG, en=TIMES, bold=False, align=None,
         indent_chars=0, space_after=0, line=1.0, color=None):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing = line
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(0)
    if indent_chars:
        pf.first_line_indent = Pt(size * indent_chars)
    if align is not None:
        p.alignment = align
    if text:
        r = p.add_run(text)
        set_run_font(r, cn, en, size, bold, color)
    return p

def h1(doc, text):
    """一级标题：四号黑体居中"""
    return para(doc, text, size=14, cn=HEI, en=HEI, bold=False,
                align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)

def h2(doc, text):
    """二级标题：小四黑体左对齐"""
    return para(doc, text, size=12, cn=HEI, en=HEI, bold=False, space_after=3)

def h3(doc, text):
    """三级标题：小四宋体加粗左对齐"""
    return para(doc, text, size=12, cn=SONG, en=TIMES, bold=True, space_after=3)

def body(doc, text, indent=True):
    """正文：小四宋体，首行缩进2字符"""
    return para(doc, text, size=12, cn=SONG, en=TIMES,
                indent_chars=2 if indent else 0, space_after=0, line=1.0)

def caption(doc, text):
    """图表题注：小四宋体居中加粗"""
    return para(doc, text, size=12, cn=SONG, en=TIMES, bold=True,
                align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)

def formula(doc, text):
    """公式行：居中，Times New Roman"""
    return para(doc, text, size=12, cn=SONG, en=TIMES,
                align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)

def add_figure(doc, path, width_cm=13.0):
    if not os.path.exists(path):
        print("  [缺图]", path)
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(path, width=Cm(width_cm))

def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:fill'), hexcolor)
    tcPr.append(shd)

def add_table(doc, headers, rows, widths=None, font_size=10.5):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, htxt in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(str(htxt))
        set_run_font(r, HEI, HEI, font_size, True)
        shade(hdr[i], "DCEBE4")   # 浅绿底（沿用用户模板绿色系）
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(str(val))
            set_run_font(r, SONG, TIMES, font_size)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    return t
