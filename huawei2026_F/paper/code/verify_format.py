#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证生成文档的格式关键要素"""
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document('docx/F题_论文.docx')

print('=== 页面设置验证 ===')
s = doc.sections[0]
checks = [
    ('页面尺寸', f'{s.page_width.cm:.2f}x{s.page_height.cm:.2f}cm', '21.00x29.70cm'),
    ('上边距', f'{s.top_margin.cm:.2f}cm', '2.54cm'),
    ('下边距', f'{s.bottom_margin.cm:.2f}cm', '2.54cm'),
    ('左边距', f'{s.left_margin.cm:.2f}cm', '3.17cm'),
    ('右边距', f'{s.right_margin.cm:.2f}cm', '3.17cm'),
]
for name, actual, expected in checks:
    status = '✅' if actual == expected else '❌'
    print(f'{status} {name}: {actual} (期望 {expected})')

print('\n=== Normal 样式验证 ===')
style = doc.styles['Normal']
font = style.font
pf = style.paragraph_format
checks = [
    ('西文字体', font.name, 'Times New Roman'),
    ('字号', f'{font.size.pt:.1f}pt' if font.size else 'None', '12.0pt'),
    ('行距', f'{pf.line_spacing:.2f}' if pf.line_spacing else 'None', '1.50'),
]
for name, actual, expected in checks:
    status = '✅' if actual == expected else '❌'
    print(f'{status} {name}: {actual} (期望 {expected})')

print('\n=== 封面关键段落验证 ===')
key_paragraphs = [
    (2, 'Logo提示行', WD_ALIGN_PARAGRAPH.CENTER, None, 12),
    (5, '大标题第1行', WD_ALIGN_PARAGRAPH.CENTER, True, 22),
    (17, '小标题第1行', WD_ALIGN_PARAGRAPH.CENTER, True, 18),
    (20, '题目行', WD_ALIGN_PARAGRAPH.CENTER, None, 14),  # 混合格式
]

for idx, label, exp_align, exp_bold, exp_size in key_paragraphs:
    p = doc.paragraphs[idx]
    act_align = p.alignment

    # 检查第一个非空 run
    first_run = None
    for r in p.runs:
        if r.text.strip():
            first_run = r
            break

    if first_run:
        act_size = first_run.font.size.pt if first_run.font.size else None
        act_bold = first_run.font.bold
    else:
        act_size = None
        act_bold = None

    align_ok = '✅' if act_align == exp_align else f'❌ (实际 {act_align})'
    size_ok = '✅' if act_size == exp_size else f'❌ (实际 {act_size}pt)'
    bold_ok = '✅' if act_bold == exp_bold else f'❌ (实际 {act_bold})'

    print(f'{label:12s} | 对齐={align_ok} 字号={size_ok} 加粗={bold_ok}')

print('\n=== 摘要验证 ===')
# 找到"摘　要："段落
abstract_title_idx = None
for i, p in enumerate(doc.paragraphs):
    if '摘　要：' in p.text:
        abstract_title_idx = i
        break

if abstract_title_idx:
    p = doc.paragraphs[abstract_title_idx]
    first_run = None
    for r in p.runs:
        if r.text.strip():
            first_run = r
            break

    if first_run:
        size = first_run.font.size.pt if first_run.font.size else None
        bold = first_run.font.bold
        align = p.alignment
        print(f'摘要标题 | 对齐={align} 字号={size}pt(期望16) 加粗={bold}(期望True)')

    # 检查第一段正文
    if abstract_title_idx + 1 < len(doc.paragraphs):
        p = doc.paragraphs[abstract_title_idx + 1]
        indent = p.paragraph_format.first_line_indent
        indent_pt = indent.pt if indent else 0
        align = p.alignment
        print(f'摘要正文 | 对齐={align}(期望JUSTIFY) 首行缩进={indent_pt:.1f}pt(期望24)')

print('\n=== 目录验证 ===')
# 找到"目　录"段落
toc_title_idx = None
for i, p in enumerate(doc.paragraphs):
    if '目　录' == p.text.strip():
        toc_title_idx = i
        break

if toc_title_idx:
    p = doc.paragraphs[toc_title_idx]
    first_run = None
    for r in p.runs:
        if r.text.strip():
            first_run = r
            break

    if first_run:
        size = first_run.font.size.pt if first_run.font.size else None
        bold = first_run.font.bold
        align = p.alignment
        print(f'目录标题 | 对齐={align} 字号={size}pt(期望16) 加粗={bold}(期望True)')

    # 检查第一个目录条目（应该是"一、问题重述"）
    if toc_title_idx + 1 < len(doc.paragraphs):
        p = doc.paragraphs[toc_title_idx + 1]
        tabs = p.paragraph_format.tab_stops
        has_tab = len(list(tabs)) > 0
        print(f'目录条目 | 制表位数量={len(list(tabs))}(期望≥1) 文本="{p.text.strip()[:20]}..."')

print('\n=== 分页符验证 ===')
page_breaks = 0
for p in doc.paragraphs:
    if hasattr(p._element, 'pPr') and p._element.pPr is not None:
        if hasattr(p._element.pPr, 'pageBreakBefore') and p._element.pPr.pageBreakBefore:
            page_breaks += 1

# 也检查 run 里的分页符
for p in doc.paragraphs:
    for r in p.runs:
        if hasattr(r._element, 'br'):
            if r._element.br is not None:
                page_breaks += 1

print(f'文档中分页符数量：{page_breaks}(期望1，在目录前)')
