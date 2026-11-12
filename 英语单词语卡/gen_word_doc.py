# -*- coding: utf-8 -*-
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
import sys, json

def set_run(run, size=11, bold=False, ascii_font='Times New Roman', ea_font='微软雅黑', color=None):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = ascii_font
    run._element.rPr.rFonts.set(qn('w:eastAsia'), ea_font)
    if color: run.font.color.rgb = RGBColor(*color)

def build(data, out):
    doc = Document()
    sec = doc.sections[0]
    sec.left_margin = sec.right_margin = Pt(50)
    st = doc.styles['Normal']
    st.font.name = 'Times New Roman'
    st.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')

    # 标题
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(p.add_run(f"📘 单词汇总 · 第 {data['no']} 个"), 16, True, 'Times New Roman', '微软雅黑', (0x1F,0x4E,0x79))

    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(p.add_run("—— 高考英语高频 800 词 ——"), 10, False, color=(0x80,0x80,0x80))

    doc.add_paragraph()

    # 单词大字
    p = doc.add_paragraph()
    set_run(p.add_run(data['word']), 22, True, 'Times New Roman', '微软雅黑', (0x1F,0x4E,0x79))
    p2 = doc.add_paragraph()
    set_run(p2.add_run(data['phonetic']), 11, False, color=(0x60,0x60,0x60))

    def section(title):
        p = doc.add_paragraph()
        p.space_before = Pt(10)
        set_run(p.add_run(title), 12, True, 'Times New Roman', '微软雅黑', (0xC0,0x50,0x4D))
        return p

    def line(text, indent=False, size=11, bold=False, color=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.3
        if indent:
            p.paragraph_format.left_indent = Pt(12)
        set_run(p.add_run(text), size, bold, color=color)
        return p

    section("英英释义")
    line(data['definition_en'])
    line(data['definition_zh'], color=(0x60,0x60,0x60))

    section("词根词缀")
    for k, v in data['roots']:
        line(f"{k}  {v}", indent=True)

    section("记忆方法")
    line(data['memory'])

    section("词性与词形变化")
    line("词性  " + data['pos'], indent=True)
    line("变形  " + data['forms'], indent=True)

    section("常见搭配")
    for i, c in enumerate(data['collocations'], 1):
        line(f"{i}. {c[0]}    {c[1]}", indent=True)

    section("例句")
    for i, (en, zh) in enumerate(data['examples'], 1):
        line(f"{i}. {en}", indent=True)
        line(f"    {zh}", indent=True, color=(0x60,0x60,0x60))

    section("⚠️ 易错提醒")
    line(data['warning'])

    doc.add_paragraph()
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(p.add_run("※ 本词已过关，可进入下一个单词"), 9, False, color=(0x99,0x99,0x99))
    doc.save(out)
    print("saved", out)

if __name__ == '__main__':
    d = json.load(open(sys.argv[1], encoding='utf-8'))
    build(d, sys.argv[2])
