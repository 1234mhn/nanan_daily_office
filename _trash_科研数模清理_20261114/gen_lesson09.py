#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第9课 · 一起去吃饭吧 —— 韩剧精讲笔记（HTML + Word 三件套内容母版）
素材：/www/korean_course/lesson9.html（只读，不修改）
样式：/www/korean_notes/lesson55.html（基准模板）
"""
import re, html as H, json, os

SRC = '/www/korean_course/lesson9.html'
T55 = '/www/korean_notes/lesson55.html'
OUT_HTML = '/www/korean_notes/lesson09.html'
OUT_DOCX = '/www/korean_notes/files/第9课韩剧精讲笔记.docx'
COURSE_TITLE = '第9课韩剧精讲笔记'
SUB = '一起去吃饭吧（晚餐邀请·拐弯抹角的好意）'


def clean(s):
    s = re.sub(r'<div[^>]*>\s*$', '', s)      # 切块残留的开头 <div>
    s = re.sub(r'<br\s*/?>', '\n', s)
    s = re.sub(r'</div>\s*<div>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    return H.unescape(s).strip()


def twoline(s):
    """每句一行的文本 → 行列表"""
    return [' '.join(l.split()) for l in s.split('\n') if l.strip()]


def parse():
    h = open(SRC, encoding='utf-8').read()
    blocks = re.findall(r'<div class="line".*?(?=<div class="line"|</body)', h, re.S)
    items = []
    for b in blocks:
        kr = clean(re.search(r'<p class="kr"[^>]*>(.*?)</p>', b, re.S).group(1))
        cn = clean(re.search(r'<p class="cn">(.*?)</p>', b, re.S).group(1)).lstrip('→ ').strip()
        en = clean(re.search(r'<p class="en"[^>]*>(.*?)</p>', b, re.S).group(1)).lstrip('→ ').strip()
        exp = b[b.find('class="line-exp"'):]

        # 单词
        words = []
        seg = exp[exp.find('📍单词') + 4:]
        seg = seg[:seg.find('💬 短语')] if '💬 短语' in seg else seg
        for m in re.finditer(r'<div><b>(.*?)</b>\s*—\s*(.*?)</div>', seg, re.S):
            words.append((clean(m.group(1)), clean(m.group(2))))

        # 短语
        phrases = []
        if '💬 短语' in exp:
            seg = exp[exp.find('💬 短语'):]
            seg = seg[:seg.find('📌 句型')] if '📌 句型' in seg else seg
            for line in twoline(clean(seg)):
                line = re.sub(r'^💬\s*短语\s*', '', line).strip()
                if line:
                    phrases.append(line)

        # 句型 + 例句（交错）
        pats = []
        if '📌 句型' in exp:
            seg = exp[exp.find('📌 句型') + len('📌 句型'):]
            seg = seg[:seg.find('class="phon"')] if 'class="phon"' in seg else seg
            seg = re.sub(r'<div[^>]*>\s*$', '', seg)   # 末尾切断残留 <div
            seg = seg.replace('</div>', '\n')
            cur_t, cur_ex = None, []
            for line in twoline(clean(seg)):
                if re.match(r'^[①②③④⑤⑥⑦⑧⑨⑩]', line):
                    if cur_t is not None:
                        pats.append([cur_t, cur_ex])
                    cur_t, cur_ex = line, []
                elif line.startswith('💬例句'):
                    cur_ex.append(re.sub(r'^💬例句\d*\s*', '', line).strip())
                elif re.fullmatch(r'<div[^>]*', line):
                    continue   # 结构残留
                elif cur_t is not None and line:
                    if cur_ex:  # 例句换行续接（→ 中文 / — English）
                        cur_ex[-1] = (cur_ex[-1] + ' ' + line).strip()
                    else:
                        cur_t = (cur_t + ' ' + line).strip()
            if cur_t is not None:
                pats.append([cur_t, cur_ex])
            pats = [(t, e) for t, e in pats]

        # 音变
        phon = ''
        m = re.search(r'class="phon">(.*?)</div>', exp, re.S)
        if m:
            pl = twoline(clean(m.group(1)))
            pl[0] = re.sub(r'^🎵\s*音变\s*', '', pl[0]) if pl else ''
            phon = ' / '.join(x for x in pl if x).strip()

        items.append(dict(kr=kr, cn=cn, en=en, words=words, phrases=phrases, pats=pats, phon=phon))

    # 句型总结（源文件 pattern9 区块）
    summary = []
    seg = h[h.find('id="pattern9"'):]
    seg = seg[:seg.find('<button class="done-toggle"')]
    for m in re.finditer(r'<b>(.*?)</b>\s*<div[^>]*>(.*?)</div>', seg, re.S):
        title = clean(m.group(1))
        dline = twoline(clean(m.group(2)))
        desc = ' '.join(dline)
        summary.append([title, desc])
    return items, summary


# ---------------- 单词汇总（只放真单词，过滤语法词尾/句型） ----------------
# 源 lesson9.html「📌 单词」里混入的语法成分（全部剔除）
DROP = {'부터', '-한테', '-면', '-도', '거', '것', '-고', '-어 주다', '안'}
# 汇总时做词形统一（原句里出现的是活用形）
NORMALIZE = {
    '저랑': ('저', '我（谦称，저+랑 和我）'),
    '내가': ('내가', '我（내+가，第一人称主格）'),
    '봤다': ('봤다', '看了（보다 的过去式）'),
}
# 汇总里额外补充的真单词（来自原句实际出现的词，源文件单词块未单列）
EXTRA = [
    ('먹다', '吃'),             # 먹을 / 먹으면 / 먹어 줄게요
    ('저녁', '晚餐'),            # 저녁 되실래요
    ('비싸다', '贵'),            # 비싼(비싸다 的定语形) 데래요
    ('맛있다', '好吃'),          # 맛있는 것
    ('호의', '好意[汉:好意]'),    # 원문 호의를 → 单词块未单列
    ('베풀다', '施予/给予'),      # 원문 베푼 건데 → 单词块未单列
    ('갚다', '偿还/还(人情)'),    # 원문 갚는 것처럼
    ('생색', '邀功[汉:生色]'),    # 원문 생색을 내지
    ('내다', '显摆/表现'),        # 원문 생색을 내지
    ('신세', '人情[汉:身世]'),    # 원문 신세 진 / 신세를 갚는
    ('지다', '欠(人情)/背负'),    # 원문 신세 진
    ('두', '二/两'),             # 두 사람 자리
]
EXTRA = [e for e in EXTRA if e[1]]


def vocab(items):
    seen, out = set(), []
    for it in items:
        for w, m in it['words']:
            if w in DROP or w in seen:
                continue
            if w.startswith('-') or w.startswith('~'):
                continue
            seen.add(w)
            if w in NORMALIZE:
                nw, nm = NORMALIZE[w]
                if nw not in seen:
                    seen.add(nw)
                    out.append((nw, nm))
                continue
            out.append((w, m))
    for w, m in EXTRA:
        if w not in seen:
            seen.add(w)
            out.append((w, m))
    return out


# ---------------- HTML ----------------
def esc(s):
    return H.escape(s)


def build_html(items, summary, words):
    css = re.search(r'<style>(.*?)</style>', open(T55, encoding='utf-8').read(), re.S).group(1)
    P = ['<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         f'<title>{COURSE_TITLE}</title><style>{css}</style></head><body><div class="page">']
    P.append('<div class="hero"><div class="eyebrow">KOREAN DRAMA · 场景台词精讲</div>')
    P.append(f'<h1>{COURSE_TITLE}</h1><div class="sub">{esc(SUB)}</div>')
    # TODO: 抖音视频链接待补（用户提供后替换 href）
    P.append('<div class="vid">🎬 相关韩语学习视频（抖音）：<a href="" target="_blank" rel="noopener">待补充</a></div>')
    P.append('<div class="hr"></div></div>')
    P.append(f'<div class="sec">台词逐句精讲 <span>{len(items)} 句</span></div>')
    for i, it in enumerate(items, 1):
        p = [f'<div class="item"><div class="kr">{i}. {esc(it["kr"])}</div>',
             f'<div class="cn">→ {esc(it["cn"])}</div>',
             f'<div class="en">→ {esc(it["en"])}</div><div class="divide"></div>']
        if it['words']:
            p.append('<div class="box"><span class="lb">📍 单词</span>' +
                     '<br>'.join(f'{esc(w)} {esc(m)}' for w, m in it['words']) + '</div>')
        if it['phrases']:
            p.append('<div class="row"><span class="lb">💬 短语</span>' + '<br>'.join(esc(x) for x in it['phrases']) + '</div>')
        # 句型与例句交错
        for k, (t, exs) in enumerate(it['pats']):
            p.append(f'<div class="row"><span class="lb">📌 句型</span>{esc(t)}</div>')
            if exs:
                p.append('<div class="box ex"><div class="exlabel">例句</div>' +
                         ''.join(f'<div class="ecline">{n}. {esc(x)}</div>' for n, x in enumerate(exs, 1)) + '</div>')
        if it['phon']:
            p.append(f'<div class="phon">🎵 音变 {esc(it["phon"])}</div>')
        p.append('</div>')
        P.append(''.join(p))

    P.append(f'<div class="sec">本课句型总结 <span>{len(summary)} 组</span></div>')
    for t, d in summary:
        # 拆出「-> 例句」部分
        main, _, ex = d.partition('->')
        P.append(f'<div class="pcard"><div class="ph2">{esc(t)}</div><div class="pd">{esc(main.strip())}</div>'
                 f'<div class="pe">→ {esc(ex.strip())}</div></div>' if ex.strip()
                 else f'<div class="pcard"><div class="ph2">{esc(t)}</div><div class="pd">{esc(main.strip())}</div></div>')

    P.append(f'<div class="sec">本课单词汇总 <span>{len(words)} 个</span></div><div class="wcols">')
    for w, m in words:
        P.append(f'<div class="witem"><b>{esc(w)}</b><span>{esc(m)}</span></div>')
    P.append('</div>')
    P.append(f'<div class="foot">场景台词精讲笔记 · 第9课 · 一起去吃饭吧</div>')
    P.append('<div class="dlbar">'
             '<a class="dlbtn" href="/korean-notes/files/第9课韩剧精讲笔记.docx" download>📄 下载 Word</a>'
             '<a class="dlbtn alt" href="/korean-notes/files/第9课韩剧精讲笔记.pdf" download>📕 下载 PDF</a>'
             '</div></div></body></html>')
    if os.path.exists(OUT_HTML):
        os.system(f'cp "{OUT_HTML}" "{OUT_HTML}.bak_20261113"')
    open(OUT_HTML, 'w', encoding='utf-8').write(''.join(P))


if __name__ == '__main__':
    items, summary = parse()
    words = vocab(items)
    build_html(items, summary, words)
    print(f'✅ HTML {OUT_HTML}')
    print(f'   台词 {len(items)} 句 / 句型总结 {len(summary)} 组 / 单词 {len(words)} 个')
    json.dump(dict(items=items, summary=summary, words=words),
              open('/root/.openclaw/workspace/l9_data.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
