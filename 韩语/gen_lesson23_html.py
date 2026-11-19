# -*- coding: utf-8 -*-
"""第23课：内容母版(lesson23_content.py) -> HTML（照 lesson07 样式原样复用）"""
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lesson23_content as C

E = lambda s: html.escape(s, quote=False)

STYLE = """@import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700;800&display=swap');
*{box-sizing:border-box}
body{margin:0;background:#fff;color:#2F3437;font-family:'Nanum Gothic','Noto Sans KR','Source Han Sans SC','PingFang SC','Microsoft YaHei',sans-serif;line-height:1.5;-webkit-font-smoothing:antialiased}
.page{max-width:700px;margin:0 auto;padding:48px 26px 70px}
.hero{margin-bottom:34px}
.eyebrow{font-size:12px;color:#9AA5AD;letter-spacing:2px;margin-bottom:8px}
.hero h1{margin:0;font-size:27px;font-weight:800;color:#1F2529}
.sub{margin-top:7px;font-size:15px;color:#5C666E}
.hr{margin-top:16px;width:40px;height:3px;background:#2F3437;border-radius:2px}
.sec{margin:34px 0 10px;font-size:19px;font-weight:800;color:#1F2529;display:flex;align-items:center;gap:10px}
.sec span{font-size:12.5px;font-weight:400;color:#B0B9C0}
.item{padding:20px 0 18px;border-top:1px solid #EDF0F2}
.item:first-of-type{border-top:none}
.kr{font-size:19px;font-weight:800;color:#1F2529;line-height:1.45}
.cn{font-size:15px;color:#4A545C;margin-top:4px}
.en{font-size:12.5px;color:#A8B2B9;font-style:italic;margin-top:2px}
.divide{height:1px;background:#F0F3F5;margin:11px 0 10px}
.box{background:#F7F9FA;border-radius:7px;padding:8px 12px;font-size:13.5px;color:#5C666E;margin:6px 0}
.row{font-size:13.5px;color:#4A545C;margin:5px 0}
.lb{color:#98A4AD;font-weight:700;margin-right:8px;font-size:12.5px}
.ph{font-size:14.5px;font-weight:700;color:#1F2529;margin-top:9px}
.pd{font-size:13.5px;color:#5C666E;margin-top:4px}
.box.ex{color:#6B747C}
.exlabel{color:#98A4AD;font-size:12.5px;font-weight:700;margin-bottom:2px}
.ecline{margin:1px 0;padding-left:.4cm}
.phon{font-size:12.5px;color:#A8B2B9;margin-top:8px}
.pcard{padding:12px 15px;margin-bottom:8px;border:1px solid #EDF0F2;border-radius:8px}
.ph2{font-size:15px;font-weight:700;color:#1F2529}
.pe{font-size:12.5px;color:#98A4AD;margin-top:5px}
.wcols{column-count:2;column-gap:18px;margin-top:6px}
.witem{break-inside:avoid;padding:7px 0;border-bottom:1px solid #F2F5F7;font-size:13.5px}
.witem b{color:#1F2529;font-weight:700;margin-right:9px}
.witem span{color:#5C666E}
.foot{margin-top:44px;padding-top:16px;border-top:1px solid #EDF0F2;text-align:center;font-size:12px;color:#B0B9C0}
.dlbar{position:fixed;right:22px;bottom:22px;display:flex;flex-direction:column;gap:9px;z-index:99}
.dlbtn{display:block;text-align:center;text-decoration:none;border-radius:26px;padding:11px 20px;font-size:14px;font-weight:700;background:#1F2529;color:#fff;box-shadow:0 4px 14px rgba(31,37,41,.22);font-family:inherit}
.dlbtn.alt{background:#fff;color:#1F2529;border:1.5px solid #DDE3E7;box-shadow:0 3px 10px rgba(31,37,41,.1)}
@media (max-width:480px){.wcols{column-count:1}.dlbar{right:12px;bottom:12px}}
@media print{.page{max-width:none;padding:0}.item,.pcard{break-inside:avoid}.dlbar{display:none}}"""

out = []
out.append('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">'
           '<meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>{E(C.TITLE)}</title><style>\n{STYLE}\n</style></head><body><div class="page">')
out.append('<div class="hero"><div class="eyebrow">KOREAN DRAMA · 场景台词精讲</div>'
           f'<h1>{E(C.TITLE)}</h1><div class="sub">{E(C.SUB)}</div><div class="hr"></div></div>')

out.append(f'<div class="sec">台词逐句精讲 <span>{len(C.LINES)} 句</span></div>')
for i, L in enumerate(C.LINES, 1):
    out.append('<div class="item">')
    out.append(f'<div class="kr">{i}. {E(L["kr"])}</div>')
    out.append(f'<div class="cn">{E(L["cn"])}</div>')
    out.append(f'<div class="en">{E(L["en"])}</div>')
    out.append('<div class="divide"></div>')
    if L["words"]:
        rows = ''.join(f'{E(w)} {E(m)}<br>' for w, m in L["words"]).rstrip('<br>')
        out.append(f'<div class="box"><div class="lb">📍 单词</div>{rows}</div>')
    for p in L["phrases"]:
        out.append(f'<div class="row"><span class="lb">💬 短语</span>{E(p[0])} — {E(p[1])}</div>')
    for p in L["patterns"]:
        out.append(f'<div class="ph">{E(p["t"])}</div>')
        out.append(f'<div class="pd">{E(p["d"])}</div>')
        ec = ''.join(f'<div class="ecline">{j}. {E(ex[0])} → {E(ex[1])}</div>'
                     for j, ex in enumerate(p["ex"], 1))
        out.append(f'<div class="box ex"><div class="exlabel">例句</div>{ec}</div>')
    out.append(f'<div class="phon">音变 {E(L["phon"])}</div>')
    out.append('</div>')

out.append(f'<div class="sec">本课句型总结 <span>{len(C.PATTERNS)} 组</span></div>')
for t, d, e in C.PATTERNS:
    out.append(f'<div class="pcard"><div class="ph2">{E(t)}</div><div class="pd">{E(d)}</div>'
               f'<div class="pe">{E(e)}</div></div>')

out.append(f'<div class="sec">本课单词汇总 <span>{len(C.WORDS)} 个</span></div>')
out.append('<div class="wcols">')
for w, m in C.WORDS:
    out.append(f'<div class="witem"><b>{E(w)}</b><span>{E(m)}</span></div>')
out.append('</div>')

out.append(f'<div class="foot">场景台词精讲笔记 · 第23课 · {E(C.SUB.split("（")[0])}</div>')
out.append('<div class="dlbar">'
           '<a class="dlbtn" href="/korean-notes/files/第23课韩剧精讲笔记.docx" download>📄 下载 Word</a>'
           '<a class="dlbtn alt" href="/korean-notes/files/第23课韩剧精讲笔记.pdf" download>📕 下载 PDF</a>'
           '</div>')
out.append('</div></body></html>')

os.makedirs('/www/korean_notes', exist_ok=True)
with open('/www/korean_notes/lesson23.html', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('written', os.path.getsize('/www/korean_notes/lesson23.html'))
