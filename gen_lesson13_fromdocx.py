#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第13课 · 按用户改定的 Word 母版重新生成 HTML/PDF
🔴 Word 是内容母版，HTML/PDF 从母版派生
"""
import re, html as H
from docx import Document

DOCX = '/www/korean_notes/files/第13课韩剧精讲笔记.docx'
OUT_HTML = '/www/korean_notes/lesson13.html'
OUT_DOCX = '/www/korean_notes/files/第13课韩剧精讲笔记.docx'
T55 = '/www/korean_notes/lesson55.html'
DOUYIN = ''  # 抖音链接（用户后发）

css = re.search(r'<style>(.*?)</style>', open(T55, encoding='utf-8').read(), re.S).group(1)

def E(s):
    return H.escape(s)

d = Document(DOCX)
paras = [p.text.rstrip() for p in d.paragraphs]

# ---------- 解析母版 ----------
items, pats = [], []
cur = None
mode = None     # None / 'item' / 'pattern'
for raw in paras:
    t = raw.strip()
    if not t:
        continue
    if t.startswith('第13课') or t == '男女主再次重逢' or t.startswith('KOREAN DRAMA'):
        continue
    if t.startswith('台词逐句精讲'):
        continue
    if t == '本课句型总结':
        mode = 'pattern'; cur = None; continue
    if t == '本课单词汇总':
        mode = 'word'; continue

    if mode == 'pattern':
        pats.append(t)
        continue
    if mode == 'word':
        continue

    m = re.match(r'^(\d+)\.\s+(.*)$', t)
    if m:
        cur = {'kr': m.group(2), 'cn': '', 'en': '', 'words': '', 'phrase': '',
               'pt': [], 'exs': []}
        items.append(cur)
        continue
    if cur is None:
        continue
    if t.startswith('→ '):
        if not cur['cn']:
            cur['cn'] = t[2:].strip()
        elif not cur['en']:
            cur['en'] = t[2:].strip()
        else:
            cur['exs'].append(t[2:].strip())
        continue
    if t.startswith('📍'):
        cur['words'] = t[1:].strip()
        continue
    if t.startswith('💬'):
        cur['phrase'] = t[1:].strip()
        continue
    if t.startswith('句型：') or t.startswith('句型:'):
        cur['pt'].append(t.replace('句型：', '').replace('句型:', '').strip())
        continue
    # 其余：句型的补充说明 / 例句
    if cur['pt']:
        # 判断是不是"句型补充说明"：含箭头/表结构描述/或纯框架词
        is_note = bool(re.search(r'→|\+|-｜|\|', t)) or t.startswith(('名词', '动词', '形容词', '动 /', '形 '))
        if not is_note and re.search(r'[가-힣]', t):
            cur['exs'].append(t.strip())
        else:
            cur['pt'].append(t.strip())
    else:
        cur['exs'].append(t.strip())

# 单词表
wl = []
if d.tables:
    for row in d.tables[0].rows:
        for c in row.cells:
            ctext = c.text.strip()
            if ctext:
                wl.append(ctext)

print(f'母版解析：台词 {len(items)} 句 / 句型总结 {len(pats)} 组 / 单词 {len(wl)} 个')

# ---------- 生成 HTML ----------
P = []
P.append('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">')
P.append('<meta name="viewport" content="width=device-width,initial-scale=1">')
P.append('<title>第13课韩剧精讲笔记</title><style>' + css + '</style></head><body><div class="page">')
P.append('<div class="hero"><div class="eyebrow">KOREAN DRAMA · 场景台词精讲</div>')
P.append('<h1>第13课韩剧精讲笔记</h1>')
P.append('<div class="sub">男女主再次重逢</div>')
if DOUYIN:
    P.append(f'<div class="vid">🎬 相关韩语学习视频（抖音）：<a href="{E(DOUYIN)}" target="_blank">{E(DOUYIN)}</a></div>')
P.append('<div class="hr"></div></div>')

P.append(f'<div class="sec">台词逐句精讲 <span>{len(items)} 句</span></div>')
for i, it in enumerate(items, 1):
    p = ['<div class="item">']
    p.append(f'<div class="kr">{i}. {E(it["kr"])}</div>')
    if it['cn']:
        p.append(f'<div class="cn">→ {E(it["cn"])}</div>')
    if it['en']:
        p.append(f'<div class="en">→ {E(it["en"])}</div>')
    p.append('<div class="divide"></div>')
    if it['words']:
        p.append(f'<div class="box"><span class="lb">📍 单词</span>{E(it["words"])}</div>')
    if it['phrase']:
        p.append(f'<div class="row"><span class="lb">💬 短语</span>{E(it["phrase"])}</div>')
    if it['pt']:
        txt = '<br>'.join(E(x) for x in it['pt'])
        p.append(f'<div class="row"><span class="lb">📌 句型</span>{txt}</div>')
    if it['exs']:
        p.append('<div class="box ex"><div class="exlabel">例句</div>' +
                 ''.join(f'<div class="ecline">{j}. {E(x)}</div>' for j, x in enumerate(it['exs'], 1)) + '</div>')
    p.append('</div>')
    P.append(''.join(p))

if pats:
    P.append(f'<div class="sec">本课句型总结 <span>{len(pats)} 组</span></div>')
    for t in pats:
        # 拆成 标题 — 说明
        if '—' in t:
            head, desc = t.split('—', 1)
            P.append(f'<div class="pcard"><div class="ph2">{E(head.strip())}</div><div class="pd">{E(desc.strip())}</div></div>')
        else:
            P.append(f'<div class="pcard"><div class="pd">{E(t)}</div></div>')

if wl:
    P.append(f'<div class="sec">本课单词汇总 <span>{len(wl)} 个</span></div><div class="wcols">')
    for w in wl:
        parts = w.split('  ', 1)
        if len(parts) == 2:
            P.append(f'<div class="witem"><b>{E(parts[0].strip())}</b><span>{E(parts[1].strip())}</span></div>')
        else:
            P.append(f'<div class="witem"><b>{E(w)}</b></div>')
    P.append('</div>')

P.append('<div class="foot">场景台词精讲笔记 · 第13课 · 男女主再次重逢</div>')
P.append('<div class="dlbar">'
         '<a class="dlbtn" href="/korean-notes/files/第13课韩剧精讲笔记.docx" download>📄 下载 Word</a>'
         '<a class="dlbtn alt" href="/korean-notes/files/第13课韩剧精讲笔记.pdf" download>📕 下载 PDF</a>'
         '</div></div></body></html>')

open(OUT_HTML, 'w', encoding='utf-8').write(''.join(P))
print('✅ HTML:', OUT_HTML)
