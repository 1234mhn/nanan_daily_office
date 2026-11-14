# -*- coding: utf-8 -*-
"""
刘栖伶 学习周报 表盘(仪表盘)式图片生成器
数据源：飞书学生成长日记表（本周 8.18-8.24 课程数据）
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
from matplotlib import font_manager

# 中文字体
for f in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
          "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]:
    font_manager.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK SC"
plt.rcParams["axes.unicode_minus"] = False

# ===== 主题色 =====
C_BG      = "#F5F7FB"   # 背景
C_NAVY    = "#1F3A5F"   # 主深蓝
C_BLUE    = "#3B82F6"   # 亮蓝
C_TEAL    = "#0EA5A4"   # 青
C_GREEN   = "#22C55E"   # 绿(闪光)
C_ORANGE  = "#F59E0B"   # 橙(建议)
C_RED     = "#EF4444"   # 红(薄弱)
C_WHITE   = "#FFFFFF"
C_GRAY    = "#64748B"
C_LIGHT   = "#E2E8F0"

fig, ax = plt.subplots(figsize=(11, 16), dpi=200)
fig.patch.set_facecolor(C_BG)
ax.set_xlim(0, 1000)
ax.set_ylim(0, 1500)
ax.axis("off")

# ===== 数据 =====
student = "刘栖伶"
week_range = "第10周 · 8月18日 — 8月24日"
grade = "高二 · 英语 · 入学基础中等"

lessons = [
    ("8/19", "第5课", "😄", C_GREEN),
    ("8/20", "第6课", "😄", C_GREEN),
    ("8/21", "第7课", "🙂", C_BLUE),
    ("8/22", "第8课", "😄", C_GREEN),
    ("8/23", "第9课", "😄", C_GREEN),
    ("8/24", "第10课", "😄", C_GREEN),
]

stats = [
    ("6", "节课", C_BLUE),
    ("9", "小时", C_TEAL),
    ("5/6", "专注", C_GREEN),
]

weekly_content = (
    "· 语法思维导图：五大基本句型、三大从句、非谓语(to do/doing/done)\n"
    "· 关系代词 vs 关系副词：when/which/where 成分判断\n"
    "· 词根系统：pose / press 两大词根家族，变形(-ion/-ive)与用法\n"
    "· 精读 pose 词根短文（逐句分析+长难句拆解）\n"
    "· 语法填空做题思路：有提示词/无提示词、线索词推断法\n"
    "· 续写专题：读文四步、细节描写句型仿写(murmur/whisper/tremble)"
)

weak_points = (
    "· 写句子「单词不会用、不知怎么组装」，需多模仿句型\n"
    "· 词根单词熟练度不足，个别需老师提示(unpostpone等)\n"
    "· 长难句结构偶尔需提示(段首there be/复合从句)\n"
    "· 续写时动词短语运用、单词拼写需强化"
)

bright_points = (
    "· 能完整复述语法思维导图框架，思路清晰\n"
    "· 续写读文找线索词越来越熟练，预判能力成熟\n"
    "· 从凭语感转向有方法、有思路做题\n"
    "· 全周课堂互动积极，多次获老师表扬"
)

next_plan = (
    "1. 复习 pose/press 词根全部单词短语，自己造句到脱口而出\n"
    "2. 完成续写两个句型句子，继续积累细节描写短语\n"
    "3. 语法填空继续按线索词法练，巩固无提示词思路\n"
    "4. 精读剩余短文段，长难句按三步法自己拆解"
)

# ===== 头部 =====
# 顶部横幅
hb = FancyBboxPatch((20, 1390), 960, 90, boxstyle="round,pad=0,rounding_size=18",
                     fc=C_NAVY, ec="none")
ax.add_patch(hb)
ax.text(60, 1445, f"{student} · 学习周报", fontsize=34, color=C_WHITE, fontweight="bold", va="center")
ax.text(60, 1408, week_range + "  |  " + grade, fontsize=17, color="#CBD5E1", va="center")
ax.text(960, 1426, "英语 · 一对一", fontsize=16, color="#94A3B8", ha="right", va="center")

# ===== 数据速览卡片 =====
cx = 60
for label, unit, color in stats:
    card = FancyBboxPatch((cx, 1280), 290, 90, boxstyle="round,pad=0,rounding_size=14",
                          fc=C_WHITE, ec=C_LIGHT, lw=2)
    ax.add_patch(card)
    ax.text(cx+145, 1335, label, fontsize=38, color=color, fontweight="bold",
            ha="center", va="center")
    ax.text(cx+145, 1298, unit, fontsize=17, color=C_GRAY, ha="center", va="center")
    cx += 320

# ===== 本周上课状态（表盘圆心排布）======
sy = 1160
tb = FancyBboxPatch((60, sy-70), 880, 130, boxstyle="round,pad=0,rounding_size=14",
                    fc=C_WHITE, ec=C_LIGHT, lw=2)
ax.add_patch(tb)
ax.text(85, sy+35, "本周上课状态", fontsize=20, color=C_NAVY, fontweight="bold", va="center")
sx = 250
for date, lesson, emo, color in lessons:
    c = Circle((sx, sy), 26, fc=color, ec="none")
    ax.add_patch(c)
    ax.text(sx, sy, emo, fontsize=18, ha="center", va="center")
    ax.text(sx, sy+45, lesson, fontsize=13, color=C_NAVY, ha="center", va="center", fontweight="bold")
    ax.text(sx, sy-42, date, fontsize=12, color=C_GRAY, ha="center", va="center")
    sx += 118

# ===== 分区卡片函数 =====
def section(y_top, title, title_color, content, box_h, align="left", tc=C_GRAY, fs=17):
    box = FancyBboxPatch((60, y_top-box_h), 880, box_h, boxstyle="round,pad=0,rounding_size=14",
                         fc=C_WHITE, ec=C_LIGHT, lw=2)
    ax.add_patch(box)
    # 标题条
    ax.add_patch(FancyBboxPatch((60, y_top-52), 880, 52, boxstyle="round,pad=0,rounding_size=14",
                                fc=title_color, ec="none"))
    ax.text(85, y_top-26, title, fontsize=20, color=C_WHITE, fontweight="bold", va="center")
    yy = y_top - 80
    for i, line in enumerate(content.split("\n")):
        ax.text(90, yy - i*34, line, fontsize=fs, color=tc, va="top", linespacing=1.0)
    return y_top - box_h - 20

# 本周内容
ys = section(1100, "◆ 本周学习内容", C_BLUE, weekly_content, 250)
# 薄弱点
ys = section(ys, "◆ 需加强的薄弱点", C_RED, weak_points, 210, tc="#B91C1C")
# 闪光点
ys = section(ys, "◆ 闪光点与进步", C_GREEN, bright_points, 180, tc="#15803D")
# 下阶段
section(ys, "◆ 下阶段学习建议", C_ORANGE, next_plan, 210, tc="#92400E")

# 底部
ax.text(500, 40, "自动生成 · 楠楠大管家", fontsize=14, color=C_GRAY, ha="center")

plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
out = "/root/.openclaw/workspace/刘栖伶_学习周报_第10周.png"
plt.savefig(out, facecolor=C_BG, bbox_inches="tight", pad_inches=0.2)
print("SAVED:", out)
