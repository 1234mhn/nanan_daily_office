#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第37/38课精讲笔记 · HTML 页面生成
🔴 内容100%取自源文件，不自行编造
🔴 兼容两种源结构：<p class="kr"> 与 line-hd 内直接文本
"""
import re, sys, html as H

T55 = '/www/korean_notes/lesson55.html'
css = re.search(r'<style>(.*?)</style>',
                open(T55, encoding='utf-8').read(), re.S).group(1)

def clean(s):
    s = re.sub(r'<br\s*/?>', '\n', s)
    s = re.sub(r'</div>\s*<div>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    return s.replace('&nbsp;', ' ').replace('&amp;', '&').strip()

def E(s):
    return H.escape(s)

def parse(path):
    h = open(path, encoding='utf-8').read()
    title = re.search(r'<title>(.*?)</title>', h)
    title = title.group(1) if title else ''
    blocks = re.findall(r'<div class="line".*?(?=<div class="line"|</body)', h, re.S)
    items = []
    for b in blocks:
        # 台词：优先 <p class="kr">，否则取 line-hd 内文本
        m = re.search(r'<p class="kr"[^>]*>(.*?)</p>', b, re.S)
        if m:
            kr = clean(m.group(1))
        else:
            m = re.search(r'<div class="line-hd"[^>]*>(.*?)</div>', b, re.S)
            if not m:
                continue
            kr = clean(m.group(1))
            kr = re.sub(r'[🔊▸]', '', kr).strip()
        kr = re.sub(r'^\d+\.\s*', '', kr).strip()
        if not kr:
            continue
        cn = re.search(r'<p class="cn">(.*?)</p>', b, re.S)
        en = re.search(r'<p class="en"[^>]*>(.*?)</p>', b, re.S)
        cnt = clean(cn.group(1)).lstrip('→ ').strip() if cn else ''
        ent = clean(en.group(1)).lstrip('→ ').strip() if en else ''

        exp = re.search(r'<div class="line-exp"[^>]*>(.*)', b, re.S)
        exp = exp.group(1) if exp else ''

        # 单词（两种结构）
        words = []
        wseg = re.search(r'📍单词(.*?)(?:<b>💬|💬 短语|$)', exp, re.S)
        if wseg:
            ws = wseg.group(1)
            for mm in re.finditer(r'<div><b>(.*?)</b>\s*—\s*(.*?)</div>', ws, re.S):
                words.append((clean(mm.group(1)), clean(mm.group(2))))
            if not words:
                for mm in re.finditer(r'<b>(.*?)</b>\s*—\s*(.*?)(?=<b>|\Z)', ws, re.S):
                    words.append((clean(mm.group(1)), clean(mm.group(2))[:60]))
        # 短语
        phrase = ''
        pseg = re.search(r'💬 短语</b>(.*?)(?=<div class="item"><b>📌|<div class="ex|<div class="phon|$)', exp, re.S)
        if pseg:
            phrase = ' '.join(clean(pseg.group(1)).split('\n')).strip()
        # 句型
        pt = ''
        qseg = re.search(r'📌句型</b>(.*?)(?=<div class="ex|<div class="phon|$)', exp, re.S)
        if qseg:
            pt = ' '.join(clean(qseg.group(1)).split('\n')).strip()
        # 例句
        exs = []
        for mm in re.finditer(r'<div class="ex">(.*?)</div>', exp, re.S):
            t = clean(mm.group(1))
            t = re.sub(r'^💬?例句\d*\s*', '', t).strip()
            if t:
                exs.append(t)
        # 音变
        phon = ''
        gseg = re.search(r'🎵 音变</b>(.*?)(?=<div class="ex|<div class="item">|$)', exp, re.S)
        if not gseg:
            gseg = re.search(r'🎵 音变(.*?)(?=<div class="item">|$)', exp, re.S)
        if gseg:
            phon = ' '.join(clean(gseg.group(1)).split('\n')).strip()
            phon = re.sub(r'^[🎵\s]*音变\s*', '', phon)

        items.append({'kr': kr, 'cn': cnt, 'en': ent, 'words': words,
                      'phrase': phrase, 'pt': pt, 'exs': exs, 'phon': phon})

    # 句型总结（原文）
    pats = []
    s0 = h.find('句型总结')
    if s0 > 0:
        seg = h[s0:s0 + 9000]
        seg = clean(seg).replace('句型总结', '', 1)
        NUM = '①②③④⑤⑥⑦⑧⑨⑩⑪⑫'
        parts = re.split(r'([' + NUM + r'])', seg)
        for i in range(1, len(parts) - 1, 2):
            body = parts[i + 1].strip()
            if not body:
                continue
            if '—' in body:
                t, d = body.split('—', 1)
                pats.append((f'{parts[i]} {t.strip()}', ' '.join(d.split())))
            else:
                pats.append((f'{parts[i]} {body[:28]}', ' '.join(body.split())[:200]))

    # 单词汇总
    seen, wl = set(), []
    for it in items:
        for w, m in it['words']:
            if w and w not in seen and len(w) < 20:
                seen.add(w); wl.append((w, m))
    return title, items, pats, wl

def build(no, path, out):
    title, items, pats, wl = parse(path)
    name = title.split('·')[-1].strip() if '·' in title else title
    P = []
    P.append('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">')
    P.append('<meta name="viewport" content="width=device-width,initial-scale=1">')
    P.append(f'<title>第{no}课韩剧精讲笔记</title><style>{css}</style></head><body><div class="page">')
    P.append('<div class="hero"><div class="eyebrow">KOREAN DRAMA · 场景台词精讲</div>')
    P.append(f'<h1>第{no}课韩剧精讲笔记</h1>')
    P.append(f'<div class="sub">{E(name)}</div><div class="hr"></div></div>')
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
            p.append('<div class="box"><span class="lb">📍 单词</span>' +
                     '<br>'.join(f'{E(w)} {E(m)}' for w, m in it['words']) + '</div>')
        if it['phrase']:
            p.append(f'<div class="row"><span class="lb">💬 短语</span>{E(it["phrase"])}</div>')
        if it['pt']:
            p.append(f'<div class="row"><span class="lb">📌 句型</span>{E(it["pt"])}</div>')
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
    if wl:
        P.append(f'<div class="sec">本课单词汇总 <span>{len(wl)} 个</span></div><div class="wcols">')
        for w, m in wl:
            P.append(f'<div class="witem"><b>{E(w)}</b><span>{E(m)}</span></div>')
        P.append('</div>')

    P.append(f'<div class="foot">场景台词精讲笔记 · 第{no}课 · {E(name)}</div>')
    P.append('<div class="dlbar">'
             f'<a class="dlbtn" href="/korean-notes/files/第{no}课韩剧精讲笔记.docx" download>📄 下载 Word</a>'
             f'<a class="dlbtn alt" href="/korean-notes/files/第{no}课韩剧精讲笔记.pdf" download>📕 下载 PDF</a>'
             '</div></div></body></html>')
    open(out, 'w', encoding='utf-8').write(''.join(P))
    print(f'✅ 第{no}课: {len(items)}句 / 句型{len(pats)}组 / 单词{len(wl)}个 → {out}')
    return items, pats, wl

if __name__ == '__main__':
    build('37', '/www/korean_course/lesson37.html', '/www/korean_notes/lesson37.html')
    build('38', '/www/korean_course/lesson38.html', '/www/korean_notes/lesson38.html')
