#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""解析官方模板精确格式规格"""
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

d = Document('源_论文模板.docx')

print('=== 页面设置 ===')
s = d.sections[0]
print(f'Page: {s.page_width.cm:.2f}x{s.page_height.cm:.2f}cm (A4)')
print(f'Margins: T={s.top_margin.cm:.2f} B={s.bottom_margin.cm:.2f} L={s.left_margin.cm:.2f} R={s.right_margin.cm:.2f}cm')

print('\n=== 段落分析 (前40段) ===')
for i, p in enumerate(d.paragraphs[:40]):
    txt = p.text.strip()[:50] if p.text.strip() else '(empty)'
    align_map = {
        None: 'None',
        WD_ALIGN_PARAGRAPH.LEFT: 'LEFT',
        WD_ALIGN_PARAGRAPH.CENTER: 'CENTER',
        WD_ALIGN_PARAGRAPH.RIGHT: 'RIGHT',
        WD_ALIGN_PARAGRAPH.JUSTIFY: 'JUSTIFY'
    }
    align = align_map.get(p.alignment, str(p.alignment))

    # 分析 runs
    runs_info = []
    for r in p.runs:
        if r.text.strip():
            sz = f'{r.font.size.pt:.1f}' if r.font.size else 'None'
            bold = 'B' if r.font.bold else ''
            name = r.font.name or ''
            runs_info.append(f'{sz}{bold}')
    runs_str = ','.join(runs_info) if runs_info else '-'

    # 首行缩进
    indent = f'{p.paragraph_format.first_line_indent.pt:.1f}pt' if p.paragraph_format.first_line_indent else '0'

    # 行距
    line_spacing = p.paragraph_format.line_spacing if hasattr(p.paragraph_format, 'line_spacing') else None
    ls_str = f'{line_spacing:.2f}' if line_spacing else 'None'

    print(f'{i:2d} | A={align:7s} indent={indent:8s} ls={ls_str:6s} runs=[{runs_str:20s}] | {txt}')

print('\n=== 样式分析 ===')
for style in d.styles:
    if 'Normal' in style.name or 'Heading' in style.name or 'Title' in style.name:
        try:
            font = style.font
            pf = style.paragraph_format if hasattr(style, 'paragraph_format') else None
            sz = f'{font.size.pt:.1f}pt' if font.size else 'None'
            name = font.name or 'None'
            bold = 'B' if font.bold else ''
            ls = pf.line_spacing if pf and hasattr(pf, 'line_spacing') else None
            ls_str = f'{ls:.2f}' if ls else 'None'
            print(f'{style.name:30s} | font={name:20s} size={sz:8s} bold={bold:1s} line_spacing={ls_str}')
        except:
            pass
