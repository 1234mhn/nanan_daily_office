#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 9 页飞书 slide XML 到 .lark-slides/plan/clip-m3gcd-deck/"""
import json, os, subprocess

OUT = os.path.dirname(os.path.abspath(__file__))
W, H = 960, 540

DARK = "rgb(36,49,65)"
GREY = "rgb(139,148,158)"
ORANGE = "rgb(200,125,20)"
BLUE = "rgb(61,111,168)"
GREEN = "rgb(46,125,91)"
LIGHT = "rgb(245,246,247)"
YELLOW = "rgb(253,248,239)"

IMG_EVO = "P7IXbGE7hoZ0wMxk0xEc5d6vnhe"
IMG_TAX = "BqYhbbUzWo3uNyx5YDxcIg8Xnfd"


def txt(x, y, w, h, content, size=16, color=DARK, bold=False, align="left",
        anchor="top", lh=1.35):
    b = ' bold="true"' if bold else ""
    return (f'<shape type="text" topLeftX="{x}" topLeftY="{y}" width="{w}" height="{h}">'
            f'<content textType="body" textAlign="{align}" verticalAlign="{anchor}" '
            f'fontSize="{size}" color="{color}"{b} lineSpacing="{lh}">'
            f'{content}</content></shape>')


def rect(x, y, w, h, fill=None, border=None, bw=1, r=8):
    f = f'<fill><fillColor color="{fill}"/></fill>' if fill else '<fill><fillColor color="rgba(255,255,255,0)"/></fill>'
    b = f'<border color="{border}" width="{bw}"/>' if border else ''
    return (f'<shape type="rect" topLeftX="{x}" topLeftY="{y}" width="{w}" height="{h}" '
            f'cornerRadius="{r}">{f}{b}</shape>')


def slide(body, bg="rgb(255,255,255)"):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<presentation xmlns="http://www.larkoffice.com/sml/2.0" width="{W}" height="{H}">
<slide>
<style><fill><fillColor color="{bg}"/></fill></style>
<data>
{body}
</data>
</slide>
</presentation>'''


slides = []

# ---------- P1 封面 ----------
p1 = (
    rect(80, 196, 44, 4, fill=ORANGE, r=2) +
    txt(80, 226, 800, 80, '<p>医学影像中的 CLIP 方法综述<br/>与 M3GCD 定位</p>',
        size=42, bold=True, color=DARK, lh=1.25) +
    txt(80, 372, 700, 60, '<p>从图文对比学习的起点，到类别语义建模的一步</p>',
        size=18, color=GREY) +
    txt(80, 460, 700, 40, '<p>汇报人：楠楠 &nbsp;|&nbsp; 课题小组会</p>', size=13, color=GREY)
)
slides.append(slide(p1))

# ---------- P2 演进时间线（整页图） ----------
p2 = (
    txt(50, 22, 700, 34, '<p>一、医学 CLIP 的发展演进（2020 → 2026）</p>',
        size=22, bold=True, color=DARK) +
    f'<img src="{IMG_EVO}" topLeftX="40" topLeftY="66" width="880" height="440"/>'
)
slides.append(slide(p2))

# ---------- P3 问题分类图（整页图） ----------
p3 = (
    txt(50, 22, 700, 34, '<p>二、四类问题：后续方法都在补什么</p>',
        size=22, bold=True, color=DARK) +
    f'<img src="{IMG_TAX}" topLeftX="60" topLeftY="68" width="840" height="432"/>'
)
slides.append(slide(p3))

# ---------- P4 CP-CLIP vs CLIP 对比 ----------
def col(x, title, color, rows):
    body = rect(x, 110, 400, 350, fill="rgb(255,255,255)", border=color, bw=2, r=10)
    body += rect(x, 110, 400, 52, fill=color, r=10)
    body += txt(x + 20, 122, 360, 30, f'<p>{title}</p>', size=17, bold=True, color="rgb(255,255,255)")
    yy = 182
    for k, v in rows:
        body += txt(x + 22, yy, 356, 26, f'<p><strong>{k}</strong></p>', size=13, color=color)
        body += txt(x + 22, yy + 24, 356, 40, f'<p>{v}</p>', size=13, color=DARK, lh=1.35)
        yy += 66
    return body

p4 = (
    txt(50, 22, 700, 34, '<p>三、CP-CLIP 与 CLIP：同一任务，两种解构</p>',
        size=22, bold=True, color=DARK) +
    txt(50, 66, 860, 30, '<p>都做「图像 + 文本」分类，靠图文对齐；差别在于文本用什么、在哪个空间做结构化。</p>',
        size=14, color=GREY) +
    col(50, "CLIP / CP-CLIP", BLUE, [
        ("文本来源", "原始医学报告，整份编码"),
        ("解构的对象", "图像空间：核心区域 + 外围区域"),
        ("对齐方式", "核心对外围分别对齐，再融合"),
        ("没做到的", "拆完就停，未建模核心与外围的关系"),
    ]) +
    col(510, "M3GCD", GREEN, [
        ("文本来源", "结构化类别描述，扩散成软标签"),
        ("解构的对象", "语义空间：类别与类别之间的关系"),
        ("对齐方式", "类别描述扩散 + 软标签监督"),
        ("差异", "从图像空间迁移到语义空间做结构化"),
    ]) +
    txt(50, 478, 860, 32, '<p>结论：CP-CLIP 拆「图内的主次」，M3GCD 拆「类别间的关联」—— 互补，不是竞争。</p>',
        size=14, bold=True, color=ORANGE)
)
slides.append(slide(p4))

# ---------- P5 创新点 / 可借鉴 ----------
def bullet(y, num, title, desc, color):
    return (rect(470, y, 34, 34, fill=color, r=17) +
            txt(470, y + 6, 34, 24, f'<p>{num}</p>', size=15, bold=True,
                color="rgb(255,255,255)", align="center") +
            txt(516, y - 2, 400, 28, f'<p>{title}</p>', size=16, bold=True, color=color) +
            txt(516, y + 26, 400, 56, f'<p>{desc}</p>', size=12.5, color=DARK, lh=1.4))

p5 = (
    txt(50, 22, 700, 34, '<p>四、可借鉴的三点 + CP-CLIP 留下的缺口</p>',
        size=22, bold=True, color=DARK) +
    f'<img src="{IMG_TAX}" topLeftX="40" topLeftY="120" width="400" height="290"/>' +
    txt(40, 420, 400, 80, '<p>（左侧为四类问题图，可替换为你自己截取的 CP-CLIP 结构图放大版）</p>',
        size=11.5, color=GREY, lh=1.4) +
    bullet(96, "1", "借它的解构思路", "先拆开、再对齐。类别描述里的核心词与位置修饰词混编，会互相稀释。", BLUE) +
    bullet(186, "2", "借它的加权思想", "核心语义词权重高、外围修饰词权重低，改动小、好实现、好验证。", GREEN) +
    bullet(276, "3", "补它的缺口", "它没做「核心与外围的关系建模」，正是 M3GCD 类别扩散能接上的一环。", ORANGE) +
    rect(470, 372, 446, 116, fill=YELLOW, border=ORANGE, bw=1.6, r=10) +
    txt(490, 386, 410, 30, '<p>一句话定位</p>', size=13, bold=True, color=ORANGE) +
    txt(490, 414, 410, 70, '<p>把结构化处理从「图像空间的主次分离」迁移到「语义空间的类别关联」，'
        '这是有据可依的迁移，不是生造创新。</p>', size=12.5, color=DARK, lh=1.45)
)
slides.append(slide(p5))

# ---------- P6 CLIP 完整链路图 ----------
def stage(x, num, title, desc, color):
    return (rect(x, 150, 156, 150, fill="rgb(255,255,255)", border=color, bw=2, r=10) +
            txt(x + 12, 162, 132, 26, f'<p>{num}</p>', size=20, bold=True, color=color) +
            txt(x + 12, 194, 132, 28, f'<p>{title}</p>', size=14.5, bold=True, color=DARK) +
            txt(x + 12, 224, 132, 70, f'<p>{desc}</p>', size=11.5, color=GREY, lh=1.4))


def arrow(x):
    return (f'<line startX="{x}" startY="225" endX="{x + 26}" endY="225">'
            f'<border color="{GREY}" width="2"/></line>')

p6 = (
    txt(50, 22, 800, 34, '<p>五、CLIP 的完整链路：从预训练到下游任务</p>',
        size=22, bold=True, color=DARK) +
    txt(50, 66, 880, 30, '<p>医学场景下每一环都有专门的改进，图中标注了论文里对应的代表方法。</p>',
        size=14, color=GREY) +
    stage(40, "①", "数据构建", "图像-报告配对<br/>（报告长、噪、不对齐）", BLUE) + arrow(198) +
    stage(224, "②", "文本处理", "抽病名、套模板<br/>MedKLIP / MedFILIP", BLUE) + arrow(382) +
    stage(408, "③", "编码对齐", "核心-外同分解<br/>GloRIA / CP-CLIP", GREEN) + arrow(566) +
    stage(592, "④", "软标签监督", "类别描述扩散<br/>M3GCD 所在环节", ORANGE) + arrow(750) +
    stage(776, "⑤", "下游任务", "分类 / 报告生成<br/>检索 / 分割", GREEN) +
    rect(40, 336, 884, 120, fill=LIGHT, r=10) +
    txt(62, 352, 840, 28, '<p>链路里的三个断点，就是过去几年论文的来源</p>', size=15, bold=True, color=DARK) +
    txt(62, 384, 840, 62,
        '<p>· ② 文本脏 → 假阴性、说法不统一（MedCLIP、MedKLIP 在补）<br/>'
        '· ③ 对齐粗 → 整图对整文（GloRIA、CP-CLIP、MedFILIP 在补）<br/>'
        '· ④ 监督弱 → 标签只有一个词（<strong>M3GCD 用类别描述 + 软标签在补</strong>）</p>',
        size=12.5, color=DARK, lh=1.5) +
    txt(40, 474, 884, 40, '<p>结论：M3GCD 不是替代前面的工作，而是补在链路末端的监督环节。</p>',
        size=14, bold=True, color=ORANGE)
)
slides.append(slide(p6))

# ---------- P7-P9 实验占位 ----------
for no, title in [(7, "六、实验结果（一）"), (8, "七、实验结果（二）"), (9, "八、实验结果（三）")]:
    body = (
        txt(50, 22, 800, 34, f'<p>{title}：待补充截图</p>', size=22, bold=True, color=DARK) +
        rect(120, 90, 720, 340, fill=LIGHT, border=GREY, bw=1.6, r=12) +
        txt(140, 220, 680, 40, '<p>此处放置实验截图</p>', size=22, bold=True,
            color=GREY, align="center") +
        txt(140, 268, 680, 60, '<p>（表格 / 曲线 / 消融结果 / 可视化对比，截图后替换本区域）</p>',
            size=13, color=GREY, align="center") +
        txt(50, 452, 860, 50, '<p>讲解要点：这一页要回答的问题是什么 → 结果说明了什么 → 与 baseline 的差距在哪。</p>',
            size=13, color=DARK, lh=1.4)
    )
    slides.append(slide(body))

# 写文件
for i, s in enumerate(slides, 1):
    with open(os.path.join(OUT, f"slide{i:02d}.xml"), "w", encoding="utf-8") as f:
        f.write(s)
print("wrote", len(slides), "slides to", OUT)
