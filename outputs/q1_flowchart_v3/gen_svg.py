# -*- coding: utf-8 -*-
"""Generate q1_flowchart_v3.svg — style aligned to reference (pure B/W, right-angle
boxes, thin dark-gray borders, straight arrows, horizontal-connector forks)."""

W = 1000
H = 2000

BORDER = "#3D3D3D"
STROKE = 1.6
FONT = "'Noto Sans CJK SC','DejaVu Sans',sans-serif"
FS = 14.5          # body font size
LINE_H = 20        # line height inside a box
PAD_Y = 9          # vertical inner padding
PAD_X = 16         # horizontal inner padding

MX = 25            # outer margin

# Column geometry: two columns for parallel branches
COLW = 400         # each parallel column width
GUTTER = 30        # gap between the two columns  (2*400 + 30 = 830)
COL_L_X = MX + (W - 2*MX - (2*COLW + GUTTER)) / 2          # left col x
COL_R_X = COL_L_X + COLW + GUTTER                          # right col x
CX = W / 2.0

# Central (main single-column) boxes span this width
CENT_W = 2*COLW + GUTTER
CENT_X = COL_L_X

out = []
def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def rect(x, y, w, h, dashes=None):
    d = f' stroke-dasharray="{dashes}"' if dashes else ''
    out.append(
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'fill="#FFFFFF" stroke="{BORDER}" stroke-width="{STROKE}"{d}/>')

def diamond(cx, cy, hw, hh):
    pts = f"{cx:.1f},{cy-hh:.1f} {cx+hw:.1f},{cy:.1f} {cx:.1f},{cy+hh:.1f} {cx-hw:.1f},{cy:.1f}"
    out.append(f'<polygon points="{pts}" fill="#FFFFFF" stroke="{BORDER}" stroke-width="{STROKE}"/>')

def text_lines(lines, cx, cy):
    """cx,cy = horizontal center + vertical center of the text block."""
    n = len(lines)
    y0 = cy - (n - 1) * LINE_H / 2.0
    for i, ln in enumerate(lines):
        out.append(
            f'<text x="{cx:.1f}" y="{y0 + i*LINE_H + FS*0.36:.1f}" '
            f'font-family="{FONT}" font-size="{FS}" fill="#000000" '
            f'text-anchor="middle">{esc(ln)}</text>')

def hline(x1, x2, y):
    out.append(f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" '
               f'stroke="{BORDER}" stroke-width="{STROKE}"/>')

def vline_arrow(x, y1, y2):
    """vertical line from y1 to y2 with filled arrowhead at y2 (downward)."""
    out.append(f'<line x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" '
               f'stroke="{BORDER}" stroke-width="{STROKE}"/>')
    a = 5.0
    out.append(f'<polygon points="{x:.1f},{y2:.1f} {x-a:.1f},{y2-2*a:.1f} {x+a:.1f},{y2-2*a:.1f}" '
               f'fill="{BORDER}"/>')

def vline(x, y1, y2):
    out.append(f'<line x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" '
               f'stroke="{BORDER}" stroke-width="{STROKE}"/>')

def arrow_left_to(x_from, y_from, x_to, y_to):
    """straight line (possibly diagonal-free: only L shapes). We only use vertical/horizontal."""
    pass

# ---- node helper: draws a box sized to text and returns (y, h) ----
def box_text(lines, x, w, y, align_center=True):
    h = 2*PAD_Y + len(lines)*LINE_H + (len(lines)-1)*0
    rect(x, y, w, h)
    text_lines(lines, x + w/2.0, y + h/2.0 - (LINE_H-FS)/2.0 + 3)
    return h

# =====================================================================
# LAYOUT (top -> down). We track a running y cursor.
# =====================================================================
y = 40

# ---------- Node 1: 开始 (single centered box) ----------
n = ["开始"]
h = 2*PAD_Y + LINE_H
w1 = 180
rect(CX - w1/2, y, w1, h)
text_lines(n, CX, y + h/2 - (LINE_H-FS)/2 + 3)
y_start = y
y_end = y + h
arrow_top = y_end
arrow_bot = y_end + 34
vline_arrow(CX, arrow_top, arrow_bot)
y = arrow_bot

# ---------- Node 2: 读取数据 (single wide box) ----------
n = ["读取A1-A3质量数据 & A4-A15配比Loss数据"]
h = 2*PAD_Y + LINE_H
rect(CENT_X, y, CENT_W, h)
text_lines(n, CX, y + h/2 - (LINE_H-FS)/2 + 3)
y_end = y + h
arrow_bot = y_end + 34
vline_arrow(CX, y_end, arrow_bot)
y = arrow_bot

# ---------- Node 3: 数据预处理 (single wide box, wrapped) ----------
n = ["数据预处理：去重、指标变换、缺失异常处理、",
     "22指标分为6语义组"]
h = 2*PAD_Y + len(n)*LINE_H
rect(CENT_X, y, CENT_W, h)
text_lines(n, CX, y + h/2 - (LINE_H-FS)/2 + 3)
y_end = y + h
arrow_bot = y_end + 34
vline_arrow(CX, y_end, arrow_bot)
y = arrow_bot

# ---------- Node 4: 组内取中位数 ----------
n = ["组内取中位数得到6组组得分 G_sg"]
h = 2*PAD_Y + LINE_H
rect(CENT_X, y, CENT_W, h)
text_lines(n, CX, y + h/2 - (LINE_H-FS)/2 + 3)
y_end = y + h
arrow_bot = y_end + 34
vline_arrow(CX, y_end, arrow_bot)
y = arrow_bot

# ---------- Node 5: 熵权法 ----------
n = ["熵权法计算各组权重 w_g → 计算文本综合质量 S_s、",
     "领域平均分 S_d"]
h = 2*PAD_Y + len(n)*LINE_H
rect(CENT_X, y, CENT_W, h)
text_lines(n, CX, y + h/2 - (LINE_H-FS)/2 + 3)
y_end = y + h
arrow_bot = y_end + 34
vline_arrow(CX, y_end, arrow_bot)
y = arrow_bot

# ---------- Node 6: 冲突强度 ----------
n = ["同域计算各指标百分位秩，计算冲突强度 c_s"]
h = 2*PAD_Y + LINE_H
rect(CENT_X, y, CENT_W, h)
text_lines(n, CX, y + h/2 - (LINE_H-FS)/2 + 3)
y_end = y + h
arrow_bot = y_end + 34
vline_arrow(CX, y_end, arrow_bot)
y = arrow_bot

# ---------- Node 7: DIAMOND  c_s ≥ δ ----------
dia_w = 300        # half width
dia_h = 62         # half height
dcx, dcy = CX, y + dia_h
diamond(dcx, dcy, dia_w, dia_h)
text_lines(["c_s ≥ δ"], dcx, dcy - (LINE_H-FS)/2 + 3)
text_lines(["( 90%分位数 )"], dcx, dcy + 20)
d_bot = dcy + dia_h

# branch: 是 -> right, 否 -> left  (per reference: horizontal connector then down)
# choose: 是 -> left column, 否 -> right column? spec says 右/下引「是」, 左/下引「否」
# => 是 goes RIGHT, 否 goes LEFT.
branch_top_y = d_bot + 30
# 否 branch (left col)
NO_X = COL_L_X + COLW/2.0
YES_X = COL_R_X + COLW/2.0

# horizontal connectors from diamond sides
# left (否): from diamond left vertex outward to left col center, then down
h_no_y = branch_top_y
h_yes_y = branch_top_y
vline(NO_X, h_no_y, h_no_y + 10)   # tiny stub (will continue via box)
vline(YES_X, h_yes_y, h_yes_y + 10)

hline(NO_X, dcx, h_no_y)
hline(dcx, YES_X, h_yes_y)
# vertical arrow down into each branch box
n_no = ["否  →  直接使用综合评分 S_s"]
n_yes = ["是  →  计算稳健秩评分 S_s*，", "标记冲突样本"]

h_no = 2*PAD_Y + len(n_no)*LINE_H
h_yes = 2*PAD_Y + len(n_yes)*LINE_H
branch_box_y = h_no_y + 18
# make both same top
vline_arrow(NO_X, h_no_y, branch_box_y)
vline(NO_X, h_no_y, branch_box_y)
vline_arrow(YES_X, h_yes_y, branch_box_y)

# fix: remove the double line for NO by drawing box after; keep arrows
rect(COL_L_X, branch_box_y, COLW, h_no)
text_lines(n_no, COL_L_X + COLW/2.0, branch_box_y + h_no/2 - (LINE_H-FS)/2 + 3)
rect(COL_R_X, branch_box_y, COLW, h_yes)
text_lines(n_yes, COL_R_X + COLW/2.0, branch_box_y + h_yes/2 - (LINE_H-FS)/2 + 3)

no_bot = branch_box_y + h_no
yes_bot = branch_box_y + h_yes
merge_y = max(no_bot, yes_bot) + 30

# right side: extend yes column down to merge line
vline(YES_X, yes_bot, merge_y)
vline(NO_X, no_bot, merge_y)
# horizontal merge line spanning both columns
hline(NO_X, YES_X, merge_y)
# arrow down from center to next node
merge_arrow_bot = merge_y + 34
vline_arrow(CX, merge_y, merge_arrow_bot)
y = merge_arrow_bot

# ---------- Node 8: 输出质量评分 ----------
n = ["输出质量评分、冲突标记结果"]
h = 2*PAD_Y + LINE_H
rect(CENT_X, y, CENT_W, h)
text_lines(n, CX, y + h/2 - (LINE_H-FS)/2 + 3)
y_end = y + h
arrow_bot = y_end + 34
vline_arrow(CX, y_end, arrow_bot)
y = arrow_bot

# ---------- Node 9: 配比预处理 ----------
n = ["配比预处理：归一化配比满足和为1；",
     "划分训练集/测试集/外推集"]
h = 2*PAD_Y + len(n)*LINE_H
rect(CENT_X, y, CENT_W, h)
text_lines(n, CX, y + h/2 - (LINE_H-FS)/2 + 3)
y_end = y + h
arrow_bot = y_end + 34
vline_arrow(CX, y_end, arrow_bot)
y = arrow_bot

# ---------- Node 10: two parallel model boxes ----------
fork_y = y
hline(NO_X, YES_X, fork_y)
vline(NO_X, fork_y, fork_y + 18)
vline(YES_X, fork_y, fork_y + 18)
m_box_y = fork_y + 18
vline_arrow(NO_X, fork_y, m_box_y)
vline_arrow(YES_X, fork_y, m_box_y)

n_l = ["和约束线性岭回归"]
n_r = ["二阶交互岭回归"]
h_m = 2*PAD_Y + LINE_H
rect(COL_L_X, m_box_y, COLW, h_m)
text_lines(n_l, COL_L_X + COLW/2.0, m_box_y + h_m/2 - (LINE_H-FS)/2 + 3)
rect(COL_R_X, m_box_y, COLW, h_m)
text_lines(n_r, COL_R_X + COLW/2.0, m_box_y + h_m/2 - (LINE_H-FS)/2 + 3)
m_bot = m_box_y + h_m
m_merge_y = m_bot + 30
vline(NO_X, m_bot, m_merge_y)
vline(YES_X, m_bot, m_merge_y)
hline(NO_X, YES_X, m_merge_y)
merge_arrow_bot = m_merge_y + 34
vline_arrow(CX, m_merge_y, merge_arrow_bot)
y = merge_arrow_bot

# ---------- Node 11: 检验 ----------
n = ["独立集测试、配对Bootstrap显著性检验、跨尺度检验"]
h = 2*PAD_Y + LINE_H
rect(CENT_X, y, CENT_W, h)
text_lines(n, CX, y + h/2 - (LINE_H-FS)/2 + 3)
y_end = y + h
arrow_bot = y_end + 34
vline_arrow(CX, y_end, arrow_bot)
y = arrow_bot

# ---------- Node 12: 输出模型指标 ----------
n = ["输出模型指标，确定模型适用边界（仅1M尺度有效）"]
h = 2*PAD_Y + LINE_H
rect(CENT_X, y, CENT_W, h)
text_lines(n, CX, y + h/2 - (LINE_H-FS)/2 + 3)
y_end = y + h
arrow_bot = y_end + 34
vline_arrow(CX, y_end, arrow_bot)
y = arrow_bot

# ---------- Node 13: 结束 ----------
n = ["结束"]
h = 2*PAD_Y + LINE_H
w13 = 180
rect(CX - w13/2, y, w13, h)
text_lines(n, CX, y + h/2 - (LINE_H-FS)/2 + 3)
y_end = y + h

# ---------- caption ----------
cap_y = y_end + 40
out.append(f'<text x="{CX:.1f}" y="{cap_y:.1f}" font-family="{FONT}" font-size="16" '
           f'fill="#000000" text-anchor="middle">图 X  问题一解题思路流程图</text>')

total_h = cap_y + 30

# =====================================================================
svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{total_h:.0f}" '
           f'viewBox="0 0 {W} {total_h:.0f}">')
svg.append(f'<rect x="0" y="0" width="{W}" height="{total_h:.0f}" fill="#FFFFFF"/>')
svg.extend(out)
svg.append('</svg>')

with open("/root/.openclaw/workspace/outputs/q1_flowchart_v3/q1_flowchart_v3.svg", "w", encoding="utf-8") as f:
    f.write("\n".join(svg))
print("total_h =", total_h)
