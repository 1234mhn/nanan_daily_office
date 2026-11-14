#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第9课韩剧精讲笔记 · Word（python-docx 原生生成）
🔴 字体分离：韩文 run = NanumGothic，中文 run = Source Han Sans SC
🔴 按字符类型拆 run，分别写 w:ascii / w:hAnsi / w:eastAsia
"""
import json, re, sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

D = json.load(open('/root/.openclaw/workspace/l9_data.json', encoding='utf-8'))
ITEMS, SUMMARY, WORDS = D['items'], D['summary'], D['words']
OUT = '/www/korean_notes/files/第9课韩剧精讲笔记.docx'

KR_FONT = 'NanumGothic'
CN_FONT = 'Source Han Sans SC'

C_KR = RGBColor(0x1F, 0x25, 0x29)
C_CN = RGBColor(0x4A, 0x54, 0x5C)
C_EN = RGBColor(0xA8, 0xB2, 0xB9)
C_LB = RGBColor(0x98, 0xA4, 0xAD)
C_PH = RGBColor(0x8A, 0x9A, 0xA8)

HANGUL = re.compile(r'[\u1100-\u11FF\u3130-\u318F\uAC00-\uD7A3]')


def seg_types(text):
    """把一段文本按 韩文 / 其它 拆成 [(kind, chunk)]，kind ∈ {'kr','cn'}"""
    out = []
    for ch in text:
        k = 'kr' if HANGUL.match(ch) else 'cn'
        if out and out[-1][0] == k:
            out[-1][1] += ch
        else:
            out.append([k, ch])
    return [(k, c) for k, c in out]


def style_run(run, kind, size, bold=False, italic=False, color=None):
    rf = run._element.get_or_add_rPr().get_or_add_rFonts()
    if kind == 'kr':
        rf.set(qn('w:ascii'), KR_FONT)
        rf.set(qn('w:hAnsi'), KR_FONT)
        rf.set(qn('w:eastAsia'), KR_FONT)
        rf.set(qn('w:cs'), KR_FONT)
    else:
        rf.set(qn('w:ascii'), CN_FONT)
        rf.set(qn('w:hAnsi'), CN_FONT)
        rf.set(qn('w:eastAsia'), CN_FONT)
        rf.set(qn('w:cs'), CN_FONT)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color is not None:
        run.font.color.rgb = color


def add(p, text, size=9.5, bold=False, italic=False, color=C_CN, force=None):
    """按字符类型拆 run 写入段落；force='kr'/'cn' 时统一字体"""
    if not text:
        return
    chunks = seg_types(text) if force is None else [(force, text)]
    for kind, chunk in chunks:
        r = p.add_run(chunk)
        style_run(r, kind, size, bold, italic, color)


def fmt(p, before=0, after=0, line=1.3, indent=None, hang=None, space_rule=None):
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line
    if indent is not None:
        pf.left_indent = Cm(indent)
    if hang is not None:
        pf.first_line_indent = Cm(-hang)
    if space_rule:
        pPr = p._element.get_or_add_pPr()
        old = pPr.find(qn('w:spacing'))
        if old is not None:
            old.set(qn('w:lineRule'), space_rule)
    return p


def shade(p, hex_fill):
    pPr = p._element.get_or_add_pPr()
    sh = OxmlElement('w:shd')
    sh.set(qn('w:val'), 'clear')
    sh.set(qn('w:color'), 'auto')
    sh.set(qn('w:fill'), hex_fill)
    pPr.append(sh)


def bottom_border(p, color='EDF0F2', sz=4):
    pPr = p._element.get_or_add_pPr()
    pbdr = OxmlElement('w:pBdr')
    b = OxmlElement('w:bottom')
    b.set(qn('w:val'), 'single'); b.set(qn('w:sz'), str(sz))
    b.set(qn('w:space'), '4'); b.set(qn('w:color'), color)
    pbdr.append(b)
    pPr.append(pbdr)


def H(level, text, no, sub=None):
    """标题段（左侧竖线用文本符号，不用表格，避免影响 Word 版式）"""
    p = doc.add_paragraph()
    fmt(p, before=18 if level == 1 else 8, after=4)
    if level == 1:
        add(p, text, 15, bold=True, color=C_KR)
        if no:
            add(p, f'   {no}', 10, color=RGBColor(0xB0, 0xB9, 0xC0))
    else:
        add(p, text, 10.5, bold=True, color=C_KR)
    return p


doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.4)
sec.top_margin = Cm(2.2); sec.bottom_margin = Cm(2.2)

st = doc.styles['Normal']
st.font.name = CN_FONT
st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn('w:eastAsia'), CN_FONT)
st.paragraph_format.line_spacing = 1.3
st.paragraph_format.space_after = Pt(0)

# ---------- 封面头 ----------
p = fmt(doc.add_paragraph(), after=2)
add(p, 'KOREAN DRAMA · 场景台词精讲', 9, color=C_LB)
p = fmt(doc.add_paragraph(), after=2)
add(p, '第9课韩剧精讲笔记', 20, bold=True, color=C_KR)
p = fmt(doc.add_paragraph(), after=6)
add(p, '一起去吃饭吧（晚餐邀请·拐弯抹角的好意）', 12, bold=True, color=RGBColor(0x5C, 0x66, 0x6E))
# TODO: 抖音视频链接待补
p = fmt(doc.add_paragraph(), before=2, after=4)
add(p, '🎬 相关韩语学习视频（抖音）：待补充', 9, color=C_CN)
p = fmt(doc.add_paragraph(), before=6, after=10)
bottom_border(p, '2F3437', 8)

# ---------- ① 台词逐句精讲 ----------
H(1, '台词逐句精讲', f'{len(ITEMS)} 句')
for i, it in enumerate(ITEMS, 1):
    p = fmt(doc.add_paragraph(), before=12, after=1)
    add(p, f'{i}. {it["kr"]}', 14, bold=True, color=C_KR)
    p = fmt(doc.add_paragraph(), after=0)
    add(p, f'→ {it["cn"]}', 10.5, color=RGBColor(0x6B, 0x74, 0x7C))
    p = fmt(doc.add_paragraph(), after=4)
    add(p, f'→ {it["en"]}', 9.5, italic=True, color=C_EN)

    if it['words']:
        p = fmt(doc.add_paragraph(), before=2, after=2)
        shade(p, 'F7F9FA')
        add(p, '📍 单词', 9.5, bold=True, color=C_LB)
        for j, (w, m) in enumerate(it['words']):
            if j == 0:
                p2 = fmt(doc.add_paragraph(), before=0, after=1, indent=0.3)
            else:
                p2 = fmt(doc.add_paragraph(), before=0, after=1, indent=0.3)
            shade(p2, 'F7F9FA')
            add(p2, w, 9.5, bold=True, color=C_KR)
            add(p2, ' ' + m, 9.5, color=C_CN)

    if it['phrases']:
        p = fmt(doc.add_paragraph(), before=2, after=1)
        add(p, '💬 短语 ', 9.5, bold=True, color=C_LB)
        add(p, '  '.join(it['phrases']), 9.5, color=C_CN)

    for t, exs in it['pats']:
        p = fmt(doc.add_paragraph(), before=2, after=1)
        add(p, '📌 句型 ', 9.5, bold=True, color=C_LB)
        add(p, t, 9.5, color=C_CN)
        for k, x in enumerate(exs, 1):
            p = fmt(doc.add_paragraph(), before=0, after=1, indent=0.4)
            add(p, f'{k}. ', 9.5, color=C_CN)
            add(p, x, 9.5, color=C_CN)

    if it['phon']:
        p = fmt(doc.add_paragraph(), before=5, after=2)
        add(p, '🎵 音变 ', 9.5, bold=True, color=C_PH)
        add(p, it['phon'], 9.5, color=C_PH)
    p = fmt(doc.add_paragraph(), before=2, after=0)
    bottom_border(p, 'EDF0F2')

# ---------- ② 本课句型总结 ----------
doc.add_paragraph()
H(1, '本课句型总结', f'{len(SUMMARY)} 组')
for t, d in SUMMARY:
    title, _, mean = t.partition(' — ')
    p = fmt(doc.add_paragraph(), before=8, after=1)
    add(p, title.strip(), 10.5, bold=True, color=C_KR)
    p = fmt(doc.add_paragraph(), after=1, indent=0.3)
    add(p, mean.strip() or title.strip(), 10.5, bold=True, color=C_KR)
    p = fmt(doc.add_paragraph(), after=2, indent=0.3)
    add(p, d, 9.5, color=RGBColor(0x6B, 0x74, 0x7C))

# ---------- ③ 本课单词汇总（两栏表格，无表头） ----------
doc.add_paragraph()
H(1, '本课单词汇总', f'{len(WORDS)} 个')
half = (len(WORDS) + 1) // 2
table = doc.add_table(rows=half, cols=2)
table.autofit = True
table.style = 'Table Grid'
# 去掉边框 → 只留下分隔感（用浅色底纹交替不需要；保持干净）
tbl = table._element
tblPr = tbl.tblPr
borders = OxmlElement('w:tblBorders')
for edge in ('top', 'left', 'bottom', 'right', 'insideH'):
    e = OxmlElement(f'w:{edge}')
    e.set(qn('w:val'), 'nil')
    borders.append(e)
for edge in ('insideV',):
    e = OxmlElement(f'w:{edge}')
    e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), '4')
    e.set(qn('w:space'), '0'); e.set(qn('w:color'), 'EDF0F2')
    borders.append(e)
tblPr.append(borders)

for idx, (w, m) in enumerate(WORDS):
    row, col = idx % half, idx // half
    cell = table.cell(row, col)
    para = cell.paragraphs[0]
    fmt(para, before=2, after=2)
    add(para, w, 9.5, bold=True, color=C_KR)
    add(para, '  ', 9.5, color=C_CN)
    add(para, m, 9.5, color=RGBColor(0x7A, 0x84, 0x8C))

# ---------- 页脚 ----------
doc.save(OUT)
print('✅ DOCX', OUT)
