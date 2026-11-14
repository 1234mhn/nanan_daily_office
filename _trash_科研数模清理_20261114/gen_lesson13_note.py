#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第13课韩剧精讲笔记 · Word 母版生成
数据源: /www/korean_course/lesson13.html
样式基准: 第55课韩剧精讲笔记.docx
铁律: 韩文 run→NanumGothic / 中文 run→Source Han Sans SC (按字符类型拆分)
"""
import re, os
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

SRC = '/www/korean_course/lesson13.html'
OUT = '/www/korean_notes/files/第13课韩剧精讲笔记.docx'

C_TITLE = RGBColor(0x1F, 0x25, 0x29)
C_BODY  = RGBColor(0x4A, 0x54, 0x5C)
C_GRAY  = RGBColor(0x98, 0xA4, 0xAD)
C_FADED = RGBColor(0xA8, 0xB2, 0xB9)

KR_FONT = 'NanumGothic'
CN_FONT = 'Source Han Sans SC'

def is_kr(ch):
    return '\uac00' <= ch <= '\ud7a3' or '\u1100' <= ch <= '\u11ff' or '\u3130' <= ch <= '\u318f'

def split_runs(text):
    """按字符类型分段: (segment, is_korean)"""
    segs = []
    for ch in text:
        k = is_kr(ch)
        if segs and segs[-1][1] == k:
            segs[-1][0] += ch
        else:
            segs.append([ch, k])
    return [(s, k) for s, k in segs]

def add_text(p, text, size=11, bold=False, color=C_BODY, italic=False):
    """按中韩字体分离添加文本"""
    for seg, k in split_runs(text):
        r = p.add_run(seg)
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = color
        r.font.name = KR_FONT if k else CN_FONT
        rpr = r._element.get_or_add_rPr()
        rf = rpr.find(qn('w:rFonts'))
        if rf is None:
            rf = rpr.makeelement(qn('w:rFonts'), {})
            rpr.append(rf)
        if k:
            rf.set(qn('w:eastAsia'), KR_FONT)
            rf.set(qn('w:ascii'), KR_FONT)
            rf.set(qn('w:hAnsi'), KR_FONT)
        else:
            rf.set(qn('w:eastAsia'), CN_FONT)
            rf.set(qn('w:ascii'), CN_FONT)
            rf.set(qn('w:hAnsi'), CN_FONT)
    return p

def para(doc, space_after=0, space_before=0, line=1.3):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(space_before)
    pf.line_spacing = line
    return p

# ---------- 解析 HTML ----------
h = open(SRC, encoding='utf-8').read()
blocks = re.findall(r'<div class="line".*?(?=<div class="line"|</body)', h, re.S)

def clean(s):
    return re.sub(r'<[^>]+>', '', s).replace('&nbsp;', ' ').strip()

lines = []
for b in blocks:
    kr = re.search(r'<p class="kr"[^>]*>(.*?)</p>', b, re.S)
    cn = re.search(r'<p class="cn">(.*?)</p>', b, re.S)
    en = re.search(r'<p class="en"[^>]*>(.*?)</p>', b, re.S)
    if not kr:
        continue
    kr_t = clean(kr.group(1))
    # 判断是否含韩文
    if not any(is_kr(c) for c in kr_t):
        continue  # 跳过纯英文行（源文件前3句污染）
    kr_t = re.sub(r'^\d+\.\s*', '', kr_t)
    cn_t = clean(cn.group(1)).lstrip('→ ').strip() if cn else ''
    en_t = clean(en.group(1)).lstrip('→ ').strip() if en else ''
    # 单词
    words = []
    wexp = re.search(r'📍单词(.*?)(?:<b>短语|</div></div>)', b, re.S)
    if wexp:
        for m in re.finditer(r'<div><b>(.*?)</b>\s*—\s*(.*?)</div>', wexp.group(1), re.S):
            words.append((clean(m.group(1)), clean(m.group(2))))
    phrase = ''
    pexp = re.search(r'<b>短语</b>\s*(.*?)</div>', b, re.S)
    if pexp:
        phrase = clean(pexp.group(1))
    lines.append({'kr': kr_t, 'cn': cn_t, 'en': en_t, 'words': words, 'phrase': phrase})

print(f'解析到 {len(lines)} 句韩语台词')

# ---------- 句型总结 ----------
pat_start = h.find('📖 句型总结')
pat_end = h.find('🎵 音变提示')
pat_raw = h[pat_start:pat_end] if pat_start > 0 else ''
pats = []
for m in re.finditer(r'<div[^>]*><b>(.*?)</b>\s*—?\s*(.*?)</div>\s*<div[^>]*>(.*?)</div>', pat_raw, re.S):
    title = clean(m.group(1)); sub = clean(m.group(2)); desc = clean(m.group(3))
    if title:
        pats.append((title, sub, desc))
if not pats:
    for m in re.finditer(r'<b>(.*?)</b>\s*—?\s*<span[^>]*>(.*?)</span>', pat_raw, re.S):
        pats.append((clean(m.group(1)), '', clean(m.group(2))))
print(f'解析到 {len(pats)} 组句型')

# ---------- 音变 ----------
phon_start = h.find('🎵 音变提示')
phon_end = h.find('✓ 已完成学习')
phons = []
if phon_start > 0:
    seg = h[phon_start:phon_end if phon_end > phon_start else phon_start+2000]
    for m in re.finditer(r'➜\s*([^<➜\n|]+?)\s*([|｜])?', seg):
        t = clean(m.group(1))
        if t and t not in phons:
            phons.append(t)
print(f'解析到 {len(phons)} 条音变')

# ---------- 生成 Word ----------
doc = Document()
sec = doc.sections[0]
sec.left_margin = Cm(2.2); sec.right_margin = Cm(2.2)
sec.top_margin = Cm(2.0); sec.bottom_margin = Cm(2.0)

# 标题
p = para(doc, space_after=2)
add_text(p, '第13课韩剧精讲笔记', size=20, bold=True, color=C_TITLE)
p = para(doc, space_after=4)
add_text(p, '男女主再次重逢', size=12, color=C_BODY)
p = para(doc, space_after=0)
add_text(p, 'KOREAN DRAMA · 场景台词精讲', size=9, color=C_GRAY)

p = para(doc, space_after=6, space_before=4)
add_text(p, '台词逐句精讲', size=15, bold=True, color=C_TITLE)
add_text(p, f'  {len(lines)} 句', size=10, color=C_GRAY)

for i, ln in enumerate(lines, 1):
    p = para(doc, space_after=1, space_before=8)
    add_text(p, f'{i}. {ln["kr"]}', size=14, bold=True, color=C_TITLE)
    if ln['cn']:
        p = para(doc, space_after=1)
        add_text(p, f'→ {ln["cn"]}', size=11, color=C_BODY)
    if ln['en']:
        p = para(doc, space_after=4)
        add_text(p, f'→ {ln["en"]}', size=9.5, color=C_FADED, italic=True)
    # 单词
    if ln['words']:
        p = para(doc, space_after=2)
        add_text(p, '📍 单词 ', size=9.5, bold=True, color=C_GRAY)
        for j, (w, m) in enumerate(ln['words']):
            if j:
                add_text(p, ' · ', size=9.5, color=C_GRAY)
            add_text(p, w, size=11, bold=True, color=C_TITLE)
            add_text(p, f' {m}', size=11, color=C_BODY)
    # 短语
    if ln['phrase']:
        p = para(doc, space_after=2)
        add_text(p, '💬 短语 ', size=9.5, bold=True, color=C_GRAY)
        add_text(p, ln['phrase'], size=11, color=C_BODY)

# 句型总结
if pats:
    p = para(doc, space_after=6, space_before=14)
    add_text(p, '本课句型总结', size=15, bold=True, color=C_TITLE)
    for title, sub, desc in pats:
        p = para(doc, space_after=1, space_before=6)
        add_text(p, title, size=12, bold=True, color=C_TITLE)
        if sub:
            add_text(p, f' — {sub}', size=9.5, color=C_GRAY)
        if desc:
            p = para(doc, space_after=2)
            add_text(p, desc, size=10, color=C_BODY)

# 音变
if phons:
    p = para(doc, space_after=6, space_before=14)
    add_text(p, '本课音变提示', size=15, bold=True, color=C_TITLE)
    for t in phons:
        p = para(doc, space_after=1)
        add_text(p, '➜ ', size=10, color=C_GRAY)
        add_text(p, t, size=10.5, color=C_BODY)

# 单词汇总表
allwords = {}
for ln in lines:
    for w, m in ln['words']:
        if w and w not in allwords and is_kr(w[0]):
            allwords[w] = m
wl = list(allwords.items())
p = para(doc, space_after=6, space_before=14)
add_text(p, '本课单词汇总', size=15, bold=True, color=C_TITLE)

rows = (len(wl) + 1) // 2
tbl = doc.add_table(rows=rows, cols=2)
tbl.style = 'Table Grid'
for idx, (w, m) in enumerate(wl):
    r, c = idx // 2, idx % 2
    cell = tbl.cell(r, c)
    cp = cell.paragraphs[0]
    add_text(cp, w, size=10.5, bold=True, color=C_TITLE)
    add_text(cp, f'  {m}', size=10.5, color=C_BODY)

doc.save(OUT)
print(f'✅ 已生成: {OUT}')
