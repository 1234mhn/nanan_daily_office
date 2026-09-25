#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
问题三 求解思路总框架图（与问题一/二终版风格一致）
—— 华为杯 2026 F 题《算力约束下提升大语言模型能力的资源配置建模》
风格：学术极简 / 全白底 / 细线 / 圆角 / 中文 Noto Sans CJK / 方形回路
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon, FancyArrowPatch as FAP
import matplotlib.font_manager as fm

FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
prop = fm.FontProperties(fname=FONT)
plt.rcParams['font.family'] = prop.get_name()
plt.rcParams['axes.unicode_minus'] = False

C_WHITE, EDGE, ARROW, TXT = 'white', '#000000', '#000000', '#000000'

# 主链尺寸
BW, BH = 6.4, 0.86
XS = 8.4
GAP = 1.480
YTOP = 17.11

MAIN = [
    ('proc', '目标函数：采用问题二广义标度律 L(N, D, Q)'),
    ('proc', '成本模型：训练 6ND + 质量提升 D[g(Q)−g(Q_min)] + 注意力 ηNDL_ctx'),
    ('proc', '设定约束：三部分开销 ≤ 预算 C，Q_min < Q ≤ 1，L_ctx 外生'),
    ('proc', '联合优化求解（SLSQP 多起点 + 对数网格穷举 交叉验证）'),
    ('dia',  'Loss 曲面是否平坦？'),
    ('proc', '确立取解准则：以吃满预算为准则选取最终配置'),
    ('proc', 'KKT 条件解析与数值验证，解析证明质量取上界'),
    ('proc', '结构转移识别：PELT 变点 + 成分切换 + 活跃集跃迁'),
    ('proc', '上下文长度 L_ctx 敏感性与成本函数对比'),
    ('proc', '输出最优资源配置与结构性转移结论'),
    ('term', '结束'),
]
DI = 4  # 菱形索引：Loss 曲面形状判断

# 左支（p ≠ p_ref）
LX = 2.60
LXW, LXH = 3.5, 0.968
LX_Y = YTOP - (DI - 0.55) * GAP
LX_TXT = '曲面平坦 → 存在多重近最优解\n改以「预算利用率最高」为准则取解'

# 右支（p ≈ p_ref）
RX = 14.20
RXW, RXH = 3.5, 0.968
RX_Y = YTOP - (DI + 0.55) * GAP
RX_TXT = '曲面陡峭 → 解唯一\n按 KKT 条件直接取最优配置'

XMAX, YMAX = 16.4, 17.6

fig, ax = plt.subplots(figsize=(11.4, 12.4), dpi=220)
ax.set_xlim(0, XMAX); ax.set_ylim(0, YMAX); ax.axis('off')


def box(x, y, w, h, text, fs=11.0, lw=1.2):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.07",
        edgecolor=EDGE, facecolor=C_WHITE, linewidth=lw, zorder=3))
    ax.text(x, y, text, ha='center', va='center', fontsize=fs, color=TXT,
            fontproperties=prop, zorder=4, linespacing=1.55)


def terminal(x, y, text, w=3.4, h=0.76):
    box(x, y, w, h, text, fs=11.5, lw=1.3)
    # 胶囊：加大圆角
    for p in ax.patches[-1:]:
        p.set_boxstyle("round,pad=0.02,rounding_size=0.32")


def diamond(x, y, w, h, text, fs=10.5):
    ax.add_patch(Polygon([(x, y + h / 2), (x + w / 2, y), (x, y - h / 2), (x - w / 2, y)],
        closed=True, edgecolor=EDGE, facecolor=C_WHITE, linewidth=1.2, zorder=3))
    ax.text(x, y, text, ha='center', va='center', fontsize=fs, color=TXT,
            fontproperties=prop, zorder=4)


def seg(p1, p2, head=False):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle='-|>' if head else '-',
        mutation_scale=13, color=ARROW, linewidth=1.2, zorder=2, shrinkA=0, shrinkB=0))


ys = [YTOP - i * GAP for i in range(len(MAIN))]
DW, DH = 3.1, 1.10

for i, (t, txt) in enumerate(MAIN):
    if t == 'dia':
        diamond(XS, ys[i], DW, DH, txt)
    elif t == 'term':
        terminal(XS, ys[i], txt)
    else:
        box(XS, ys[i], BW, BH, txt)

# 主轴竖直箭头
for i in range(len(MAIN) - 1):
    if i == DI:
        continue
    seg((XS, ys[i] - BH / 2), (XS, ys[i + 1] + BH / 2), head=True)

yd = ys[DI]

# --- 菱形 → 左支（否）---
box(LX, LX_Y, LXW, LXH, LX_TXT, fs=9.8)
seg((XS - DW / 2, yd), (LX + LXW / 2 - 0.00, yd))
seg((LX, yd), (LX, LX_Y + LXH / 2), head=True)
ax.text((XS - DW / 2 + LX) / 2, yd + 0.10, '否', ha='center', va='bottom',
        fontsize=10.5, fontproperties=prop, zorder=6)

# --- 菱形 → 右支（是）---
box(RX, RX_Y, RXW, RXH, RX_TXT, fs=9.8)
seg((XS + DW / 2, yd), (RX, yd))
seg((RX, yd), (RX, RX_Y + RXH / 2), head=True)
ax.text((XS + DW / 2 + RX) / 2, yd + 0.10, '是', ha='center', va='bottom',
        fontsize=10.5, fontproperties=prop, zorder=6)

# === 汇合：左右支下沿 → 方形回路 → 汇入主轴 ===
# 左支：下 → 横线向右 → 主轴竖线
seg((LX, LX_Y - LXH / 2), (LX, ys[DI + 1]))
seg((LX, ys[DI + 1]), (XS, ys[DI + 1]))
# 右支：下 → 横线向左 → 主轴竖线（略下错开，避免与左线重叠）
merge_y2 = ys[DI + 1] - 0.36
seg((RX, RX_Y - RXH / 2), (RX, merge_y2))
seg((RX, merge_y2), (XS, merge_y2))
# 主轴：从汇合处向下到下一节点
seg((XS, ys[DI + 1]), (XS, ys[DI + 2] + BH / 2), head=True)

# 汇合点小圆点
for yy in (ys[DI + 1], merge_y2):
    ax.plot([XS], [yy], marker='o', markersize=3.4, color=ARROW, zorder=5)

plt.subplots_adjust(left=0.005, right=0.995, top=0.995, bottom=0.005)
out = '/root/.openclaw/workspace/huawei2026_F/paper/流程图_问题三_总框架'
plt.savefig(out + '.png', dpi=220, bbox_inches='tight', facecolor='white')
plt.savefig(out + '.pdf', bbox_inches='tight', facecolor='white')
print('OK ->', out)

print('\n--- 自检 ---')
print('节点数=%d  顶节点 y=%.2f  底节点 y=%.2f' % (len(MAIN), ys[0], ys[-1]))
print('左支 y=%.2f (下沿 %.2f)  右支 y=%.2f (下沿 %.2f)' % (LX_Y, LX_Y - LXH / 2, RX_Y, RX_Y - RXH / 2))
print('两条汇合横线 y=%.2f / y=%.2f' % (ys[DI + 1], ys[DI + 1] - 0.36))
print('顶部余量=%.2f  底部余量=%.2f' % (YMAX - (ys[0] + 0.38), ys[-1] - 0.38))
print('左支文字框宽=%.1f (最大行宽约 %.1f 字宽)' % (LXW, LXW / (9.8 / 72) * 1.0))
