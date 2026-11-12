#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第13课精讲笔记 · HTML 页面生成 v2
🔴 铁律：内容100%取自源文件 lesson13.html（句型/例句/音变），不自行编造
"""
import re, html as H

SRC = '/www/korean_course/lesson13.html'
OUT = '/www/korean_notes/lesson13.html'
T55 = '/www/korean_notes/lesson55.html'

src = open(SRC, encoding='utf-8').read()
t55 = open(T55, encoding='utf-8').read()
css = re.search(r'<style>(.*?)</style>', t55, re.S).group(1)

def is_kr(ch):
    return '\uac00' <= ch <= '\ud7a3' or '\u1100' <= ch <= '\u11ff' or '\u3130' <= ch <= '\u318f'

def clean(s):
    s = re.sub(r'<br\s*/?>', '\n', s)
    s = re.sub(r'</div>\s*<div>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    return s.replace('&nbsp;', ' ').replace('&amp;', '&').strip()

def E(s):
    return H.escape(s)

# ---------- 逐句解析 ----------
blocks = re.findall(r'<div class="line".*?(?=<div class="line"|</body)', src, re.S)
items = []
for b in blocks:
    kr = re.search(r'<p class="kr"[^>]*>(.*?)</p>', b, re.S)
    if not kr:
        continue
    krt = clean(kr.group(1))
    krt = re.sub(r'^\d+\.\s*', '', krt)
    if not krt:
        continue
    cn = re.search(r'<p class="cn">(.*?)</p>', b, re.S)
    en = re.search(r'<p class="en"[^>]*>(.*?)</p>', b, re.S)
    cnt = clean(cn.group(1)).lstrip('→ ').strip() if cn else ''
    ent = clean(en.group(1)).lstrip('→ ').strip() if en else ''

    exp = re.search(r'<div class="line-exp"[^>]*>(.*)', b, re.S)
    exp = exp.group(1) if exp else ''

    # 单词
    words = []
    wexp = re.search(r'📍单词(.*?)(?:<b>短语|</div></div></div>)', exp, re.S)
    if wexp:
        for m in re.finditer(r'<div><b>(.*?)</b>\s*—\s*(.*?)</div>', wexp.group(1), re.S):
            words.append((clean(m.group(1)), clean(m.group(2))))
    # 短语
    phrase = ''
    pexp = re.search(r'<b>短语</b>\s*(.*?)(?:</div><div|</div></div>)', exp, re.S)
    if pexp:
        phrase = clean(pexp.group(1)).replace('\n', '｜')
    # 句型（原文照搬）
    pt = ''
    pidx = exp.find('📌句型')
    if pidx < 0:
        pidx = exp.find('📌 句型')
    if pidx >= 0:
        rest = exp[pidx:]
        pidx2 = rest.find('🎵')
        if pidx2 > 0:
            rest = rest[:pidx2]
        midx = rest.find('例句')
        pt = clean(rest[:midx] if midx > 0 else rest).replace('📌句型', '')
    # 例句
    exs = []
    midx = exp.find('例句')
    if midx >= 0:
        seg = exp[midx:]
        eidx = seg.find('🎵')
        if eidx > 0:
            seg = seg[:eidx]
        seg = clean(seg).replace('例句', '')
        for ln in seg.split('\n'):
            ln = ln.strip()
            if ln and ln.startswith(('1.', '2.', '3.', '4.', '·')):
                exs.append(ln.lstrip('·').strip())
    # 音变
    phon = ''
    gidx = exp.find('音变', exp.find('🎵') if '🎵' in exp else 0)
    if gidx >= 0:
        seg = exp[gidx:]
        seg = clean(seg).replace('音变', '', 1)
        for stop in ['✓ 已完成', '✏️', 'js', 'function']:
            if stop in seg:
                seg = seg.split(stop)[0]
        phon = ' '.join(seg.split('\n')).strip()

    items.append({'kr': krt, 'cn': cnt, 'en': ent, 'words': words,
                  'phrase': phrase, 'pt': pt, 'exs': exs, 'phon': phon})

# ---------- 句型总结（原文，按 ①-⑪ 分块） ----------
s0 = src.find('📖 句型总结')
s1 = src.find('🎵 音变提示')
pseg = clean(src[s0:s1] if s0 > 0 and s1 > s0 else '').replace('📖 句型总结', '')
NUM = '①②③④⑤⑥⑦⑧⑨⑩⑪⑫'
pats = []
parts = re.split(r'([' + NUM + r'])', pseg)
# parts: ['', '①', ' -니 vs -니까 — 原因接口都表...', '②', ' -다고요? — ...', ...]
for i in range(1, len(parts) - 1, 2):
    num, body = parts[i], parts[i + 1].strip()
    if not body:
        continue
    # 去掉开头导语
    body = re.sub(r'^\*\*', '', body)
    if '—' in body:
        title, desc = body.split('—', 1)
        pats.append((f'{num} {title.strip()}', ' '.join(desc.split())))
    else:
        pats.append((f'{num} {body[:30]}', ' '.join(body.split())))
print('句型原文解析:', len(pats))
for t, d in pats:
    print('  ', t, '|', d[:50])

# ---------- 音变提示（原文） ----------
v0 = src.find('🎵 音变提示')
v1 = src.find('✓ 已完成学习')
phons = []
if v0 > 0:
    seg = clean(src[v0:v1 if v1 > v0 else v0 + 2500]).replace('🎵 音变提示', '')
    for ln in seg.split('\n'):
        ln = ln.strip().lstrip('➜').strip()
        if ln and len(ln) > 3:
            phons.append(ln)

# ---------- 单词汇总（原文） ----------
seen, wl = set(), []
for it in items:
    for w, m in it['words']:
        if w and w not in seen and any(is_kr(c) for c in w):
            seen.add(w); wl.append((w, m))

print(f'台词{len(items)}句 / 句型{len(pats)}组 / 音变{len(phons)}条 / 单词{len(wl)}个')

# ---------- 组装 ----------
P = []
P.append('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">')
P.append('<meta name="viewport" content="width=device-width,initial-scale=1">')
P.append('<title>第13课韩剧精讲笔记</title><style>' + css + '</style></head><body><div class="page">')
P.append('<div class="hero"><div class="eyebrow">KOREAN DRAMA · 场景台词精讲</div>')
P.append('<h1>第13课韩剧精讲笔记</h1>')
P.append('<div class="sub">男女主再次重逢（다시 만남）</div>')
P.append('<div class="hr"></div></div>')

P.append(f'<div class="sec">台词逐句精讲 <span>{len(items)} 句</span></div>')
for idx, it in enumerate(items, 1):
    p = ['<div class="item">']
    p.append(f'<div class="kr">{idx}. {E(it["kr"])}</div>')
    if it['cn']:
        p.append(f'<div class="cn">→ {E(it["cn"])}</div>')
    if it['en']:
        p.append(f'<div class="en">→ {E(it["en"])}</div>')
    p.append('<div class="divide"></div>')
    if it['words']:
        p.append('<div class="box"><span class="lb">📍 单词</span>' +
                 '<br>'.join(f'{E(w)} {E(m)}' for w, m in it['words']) + '</div>')
    if it['phrase']:
        p.append(f'<div class="row"><span class="lb">💬 短语</span>{E(it["phrase"])}</div>')
    if it['pt']:
        p.append(f'<div class="row"><span class="lb">📌 句型</span>{E(it["pt"]).replace(chr(10), "<br>")}</div>')
    if it['exs']:
        p.append('<div class="box ex"><div class="exlabel">例句</div>' +
                 ''.join(f'<div class="ecline">{E(x)}</div>' for x in it['exs']) + '</div>')
    if it['phon']:
        p.append(f'<div class="phon">🎵 音变 {E(it["phon"])}</div>')
    p.append('</div>')
    P.append(''.join(p))

if pats:
    P.append(f'<div class="sec">本课句型总结 <span>{len(pats)} 组</span></div>')
    for t, d in pats:
        P.append(f'<div class="pcard"><div class="ph2">{E(t)}</div><div class="pd">{E(d)}</div></div>')

if phons:
    P.append(f'<div class="sec">本课音变提示 <span>{len(phons)} 条</span></div>')
    for t in phons:
        P.append(f'<div class="pcard"><div class="pd">➜ {E(t)}</div></div>')

P.append(f'<div class="sec">本课单词汇总 <span>{len(wl)} 个</span></div><div class="wcols">')
for w, m in wl:
    P.append(f'<div class="witem"><b>{E(w)}</b><span>{E(m)}</span></div>')
P.append('</div>')

P.append('<div class="foot">场景台词精讲笔记 · 第13课 · 男女主再次重逢</div>')
P.append('<div class="dlbar">'
         '<a class="dlbtn" href="/korean-notes/files/第13课韩剧精讲笔记.docx" download>📄 下载 Word</a>'
         '<a class="dlbtn alt" href="/korean-notes/files/第13课韩剧精讲笔记.pdf" download>📕 下载 PDF</a>'
         '</div></div></body></html>')

open(OUT, 'w', encoding='utf-8').write(''.join(P))
print('✅', OUT)
