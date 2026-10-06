# -*- coding: utf-8 -*-
"""Patch index.html: append 场景22 card + fix theme count. Targeted edits only."""
import io, shutil

p='/www/korean_course/index.html'
s=open(p,encoding='utf-8').read()
orig=s

# ---- Edit A: fix theme count text ----
oldA='点开看该场景下的课程 · 共 17 个主题'
newA='点开看该场景下的课程 · 共 22 个主题'
assert s.count(oldA)==1, f"theme count anchor count={s.count(oldA)}"
s=s.replace(oldA,newA)

# ---- Edit B: append scene22 card after scene21 card ----
# anchor = scene21 card block (unique)
scene21='<div class="card" style="width:100%">\n<div class="ep-header" onclick="this.classList.toggle(\'open\');var c=this.nextElementSibling;if(c)c.classList.toggle(\'open\')"><span class="icon" style="display:inline-block;width:24px;text-align:left;font-size:18px;margin-right:8px;flex:none">🌌</span> 场景21 · 不想看见极光 <span class="ep-arrow" style="margin-left:auto;font-size:12px;transition:transform .3s">▶</span></div>\n<div class="ep-content">\n<a href="lesson54.html" style="display:flex;align-items:center;padding:13px 18px;border-bottom:1px solid #f5f5f5;cursor:pointer;text-decoration:none;color:#333"><span class="num" style="width:26px;height:26px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;background:#667eea;color:#fff;margin-right:12px;flex:none">1</span><span>不想看见极光</span></a>\n</div>\n</div>'
assert s.count(scene21)==1, f"scene21 anchor count={s.count(scene21)}"

scene22=scene21+'''
<div class="card" style="width:100%">
<div class="ep-header" onclick="this.classList.toggle('open');var c=this.nextElementSibling;if(c)c.classList.toggle('open')"><span class="icon" style="display:inline-block;width:24px;text-align:left;font-size:18px;margin-right:8px;flex:none">🍺</span> 场景22 · 失恋喝酒 <span class="ep-arrow" style="margin-left:auto;font-size:12px;transition:transform .3s">▶</span></div>
<div class="ep-content">
<a href="lesson61.html" style="display:flex;align-items:center;padding:13px 18px;border-bottom:1px solid #f5f5f5;cursor:pointer;text-decoration:none;color:#333"><span class="num" style="width:26px;height:26px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;background:#667eea;color:#fff;margin-right:12px;flex:none">1</span><span>失恋喝酒</span></a>
</div>
</div>'''
s=s.replace(scene21,scene22)

assert s!=orig
open(p,'w',encoding='utf-8').write(s)
print("OK. delta bytes:", len(s)-len(orig))
print("theme count:", s.count('共 22 个主题'), "| scene22:", s.count('场景22 · 失恋喝酒'), "| lesson61 link:", s.count('lesson61.html'))
