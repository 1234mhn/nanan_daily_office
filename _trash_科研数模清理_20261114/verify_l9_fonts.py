#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""字体分离验证：逐 run 检查 w:ascii / w:eastAsia，确认韩文用 NanumGothic、中文用 Source Han Sans SC"""
import re, sys
from docx import Document
from docx.oxml.ns import qn

PATH = sys.argv[1] if len(sys.argv) > 1 else '/www/korean_notes/files/第9课韩剧精讲笔记.docx'
KR, CN = 'NanumGothic', 'Source Han Sans SC'
HANGUL = re.compile(r'[\u1100-\u11FF\u3130-\u318F\uAC00-\uD7A3]')

d = Document(PATH)
bad, total, stats = [], 0, {}
def check(run, where):
    global total
    t = run.text
    if not t.strip():
        return
    total += 1
    rpr = run._element.rPr
    rf = rpr.rFonts if rpr is not None else None
    a = rf.get(qn('w:ascii')) if rf is not None else None
    e = rf.get(qn('w:eastAsia')) if rf is not None else None
    h = rf.get(qn('w:hAnsi')) if rf is not None else None
    has_kr, has_cn = bool(HANGUL.search(t)), bool(re.search(r'[^\u1100-\u11FF\u3130-\u318F\uAC00-\uD7A3]', t))
    kind = 'kr' if has_kr and not has_cn else ('mixed' if has_kr and has_cn else 'cn')
    stats[kind] = stats.get(kind, 0) + 1
    ok = (a == e == h) and (a in (KR, CN))
    if kind == 'mixed':
        ok = False
    if kind == 'kr' and a != KR:
        ok = False
    if kind == 'cn' and a != CN:
        ok = False
    if not ok:
        bad.append((where, kind, repr(t[:40]), a, h, e))

for i, p in enumerate(d.paragraphs):
    for r in p.runs:
        check(r, f'P{i}')
for ti, tb in enumerate(d.tables):
    for ri, row in enumerate(tb.rows):
        for ci, cell in enumerate(row.cells):
            for p in cell.paragraphs:
                for r in p.runs:
                    check(r, f'T{ti}R{ri}C{ci}')

print(f'文件: {PATH}')
print(f'非空 run 总数: {total}')
print('分类统计:', stats)
print(f'异常 run 数: {len(bad)}')
for b in bad[:30]:
    print('  ✗', b)
# 抽样展示
print('\n抽样（前 3 段 + 单词表首格）:')
for i in (4, 5, 6):
    for r in d.paragraphs[i].runs[:6]:
        rpr = r._element.rPr; rf = rpr.rFonts if rpr is not None else None
        print(f'  P{i}', repr(r.text[:24]), '| ascii=', rf.get(qn('w:ascii')) if rf is not None else None,
              '| eastAsia=', rf.get(qn('w:eastAsia')) if rf is not None else None)
c = d.tables[0].cell(0, 0)
for r in c.paragraphs[0].runs:
    rpr = r._element.rPr; rf = rpr.rFonts if rpr is not None else None
    print('  T0', repr(r.text[:24]), '| ascii=', rf.get(qn('w:ascii')) if rf is not None else None,
          '| eastAsia=', rf.get(qn('w:eastAsia')) if rf is not None else None)
print('\n结果:', '✅ 全部通过（韩文=NanumGothic / 中文=Source Han Sans SC）' if not bad else '❌ 存在异常')
sys.exit(1 if bad else 0)
