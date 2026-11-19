# -*- coding: utf-8 -*-
"""第23课韩剧精讲笔记 —— python-docx 原生生成（不做任何转换）"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

import lesson23_content as C

HAN = "NanumGothic"
CN = "Source Han Sans SC"

DARK = RGBColor(0x1F, 0x25, 0x29)
MID = RGBColor(0x4A, 0x54, 0x5C)
GREY = RGBColor(0xA8, 0xB2, 0xB9)
LABEL = RGBColor(0x98, 0xA4, 0xAD)

KR_RE = re.compile(r'[\u1100-\u11FF\u3130-\u318F\uA960-\uA97F\uAC00-\uD7A3]')


def is_kr(ch):
    return bool(KR_RE.match(ch))


def split_runs(text):
    """按字符类型切块：韩文字符（含韩文标点间距）一组，其余一组。"""
    out = []
    for ch in text:
        t = 'kr' if is_kr(ch) else 'cn'
        if out and out[-1][0] == t:
            out[-1][1] += ch
        else:
            out.append([t, ch])
    return [(t, s) for t, s in out]


def set_font(run, kind, size, bold=False, italic=False, color=None):
    f = HAN if kind == 'kr' else CN
    run.font.name = f
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color is not None:
        run.font.color.rgb = color
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.insert(0, rFonts)
    for a in ('w:ascii', 'w:hAnsi', 'w:eastAsia', 'w:cs'):
        rFonts.set(qn(a), f)
    # 中文 run 关掉韩文自动字体替换
    if kind == 'cn':
        lang = OxmlElement('w:lang')
        lang.set(qn('w:eastAsia'), 'zh-CN')
        rPr.append(lang)


def add_text(p, text, size, color, bold=False, italic=False):
    for kind, seg in split_runs(text):
        r = p.add_run(seg)
        set_font(r, kind, size, bold=bold, italic=italic, color=color)
    return p


def shade(p, fill="F7F9FA"):
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill)
    pPr.append(shd)


def P(doc, before=0, after=0, ls=None, indent=None, align=None):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    if ls is not None:
        pf.line_spacing = ls
    if indent is not None:
        pf.left_indent = Cm(indent)
    if align is not None:
        p.alignment = align
    return p


def cell_borders_none(table):
    tbl = table._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement('w:tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        el = OxmlElement('w:' + edge)
        el.set(qn('w:val'), 'nil')
        borders.append(el)
    tblPr.append(borders)


def cell_cell_margins(table, l=0, r=0):
    tblPr = table._tbl.tblPr
    mar = OxmlElement('w:tblCellMar')
    for edge, v in (('left', l), ('right', r)):
        el = OxmlElement('w:' + edge)
        el.set(qn('w:w'), str(v))
        el.set(qn('w:type'), 'dxa')
        mar.append(el)
    tblPr.append(mar)


def build(out_path):
    doc = Document()

    # 页面
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Emu(7772400), Emu(10058400)
    sec.left_margin = sec.right_margin = Cm(2.2)
    sec.top_margin = Cm(2.0)
    sec.bottom_margin = Cm(2.0)

    st = doc.styles['Normal']
    st.font.name = CN
    st.font.size = Pt(11)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), CN)

    # ---------- 头部 ----------
    p = P(doc, 0, 2)
    add_text(p, "KOREAN DRAMA · 场景台词精讲", 9, LABEL, bold=True)

    p = P(doc, 0, 4)
    add_text(p, C.TITLE, 22, DARK, bold=True)

    p = P(doc, 0, 2)
    add_text(p, C.SUB, 13, MID)

    p = P(doc, 4, 6)
    add_text(p, "台词逐句精讲", 14, DARK, bold=True)
    add_text(p, "  %d 句" % len(C.LINES), 10, LABEL)

    # ---------- 逐句 ----------
    for i, L in enumerate(C.LINES, start=1):
        # 韩语句：序号 + 韩文，按字符拆 run
        p = P(doc, 12, 3, ls=1.3)
        r = p.add_run("%d. " % i)
        set_font(r, 'cn', 14, bold=True, color=DARK)
        for kind, seg in split_runs(L['kr']):
            r = p.add_run(seg)
            set_font(r, kind, 14, bold=True, color=DARK)

        p = P(doc, 0, 1)
        add_text(p, L['cn'], 11, MID)

        p = P(doc, 0, 6)
        add_text(p, L['en'], 9.5, GREY, italic=True)

        # 📍 单词 标签（浅灰底）
        p = P(doc, 4, 2)
        shade(p)
        add_text(p, "📍 单词", 9.5, LABEL, bold=True)

        for w, m in L['words']:
            p = P(doc, 0, 0, ls=1.3)
            shade(p)
            add_text(p, w, 10, MID)
            add_text(p, "  " + m, 10, MID)

        # 💬 短语
        if L['phrases']:
            p = P(doc, 3, 1, ls=1.3)
            add_text(p, "💬 短语 ", 9.5, LABEL, bold=True)
            for phr, m in L['phrases']:
                add_text(p, phr, 10, MID)
                add_text(p, " — " + m, 10, MID)
                if (phr, m) != L['phrases'][-1]:
                    add_text(p, "   ｜   ", 10, MID)

        # 📌 句型（交错渲染：句型1→例句→句型2→例句）
        for j, pat in enumerate(L['patterns']):
            p = P(doc, 3 if j == 0 else 2, 1, ls=1.3)
            add_text(p, "📌 句型 " if j == 0 else "", 9.5, LABEL, bold=True)
            add_text(p, pat['t'], 10, DARK, bold=True)
            if pat['d']:
                add_text(p, "：" + pat['d'], 10, MID)
            for k, (hs, hm) in enumerate(pat['ex'], start=1):
                p = P(doc, 0, 0, ls=1.3, indent=0.4)
                add_text(p, "%d. " % k, 10, MID)
                add_text(p, hs, 10, MID)
                add_text(p, " → " + hm, 10, MID)

        # 🎵 音变
        p = P(doc, 3, 5, ls=1.3)
        add_text(p, "🎵 音变 ", 9.5, LABEL, bold=True)
        add_text(p, L['phon'], 9.5, GREY)

    # ---------- 句型总结 ----------
    p = P(doc, 14, 4)
    add_text(p, "本课句型总结", 14, DARK, bold=True)
    add_text(p, "  %d 组" % len(C.PATTERNS), 10, LABEL)

    for name, desc, ex in C.PATTERNS:
        p = P(doc, 5, 0, ls=1.3, indent=0.2)
        add_text(p, name, 11, DARK, bold=True)
        p = P(doc, 0, 0, ls=1.3, indent=0.2)
        add_text(p, desc, 10, MID)
        p = P(doc, 0, 0, ls=1.3, indent=0.2)
        add_text(p, ex, 9.5, GREY)

    # ---------- 单词汇总 ----------
    p = P(doc, 14, 4)
    add_text(p, "本课单词汇总", 14, DARK, bold=True)
    add_text(p, "  %d 个" % len(C.WORDS), 10, LABEL)

    ws = C.WORDS
    half = (len(ws) + 1) // 2
    rows = half
    table = doc.add_table(rows=rows, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    cell_borders_none(table)
    cell_cell_margins(table, 0, 60)
    for r_i in range(rows):
        for c_i in range(2):
            idx = c_i * half + r_i
            cell = table.cell(r_i, c_i)
            cp = cell.paragraphs[0]
            cp.paragraph_format.space_before = Pt(2)
            cp.paragraph_format.space_after = Pt(2)
            if idx < len(ws):
                w, m = ws[idx]
                r1 = cp.add_run(w)
                set_font(r1, 'kr', 10.5, bold=True, color=DARK)
                r2 = cp.add_run("  " + m)
                set_font(r2, 'cn', 9.5, color=MID)

    # 页脚行
    p = P(doc, 14, 0)
    add_text(p, "场景台词精讲笔记 · 第23课 · 道歉与和解", 9, GREY)

    doc.save(out_path)
    return out_path


if __name__ == '__main__':
    out = sys.argv[1]
    print(build(out))
