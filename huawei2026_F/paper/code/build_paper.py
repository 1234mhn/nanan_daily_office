# -*- coding: utf-8 -*-
"""F题论文 —— 严格对标官方模板 26106430020_1.docx
分页结构：封面+摘要+关键词(自然流) →[分页]→ 目录 →[分页]→ 正文 →[分页]→ 参考文献 →[分页]→ 附录
"""
import os
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(BASE, "..", "figures")
OUT = os.path.join(BASE, "..", "docx", "F题_论文.docx")

EN = "Times New Roman"; CN_BODY = "宋体"; CN_HEAD = "黑体"

def _rf(run, cn, size, bold=False, color=None):
    run.font.name = EN
    rPr = run._element.get_or_add_rPr()
    rf = rPr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts'); rPr.insert(0, rf)
    rf.set(qn('w:ascii'), EN); rf.set(qn('w:hAnsi'), EN); rf.set(qn('w:eastAsia'), cn)
    run.font.size = Pt(size); run.bold = bold
    if color: run.font.color.rgb = color
    return run

def P(doc, text="", size=12, cn=CN_BODY, bold=False, align=None,
      indent_pt=0, line=1.5, sa=0, sb=0):
    p = doc.add_paragraph(); pf = p.paragraph_format
    pf.line_spacing = line; pf.space_after = Pt(sa); pf.space_before = Pt(sb)
    if indent_pt: pf.first_line_indent = Pt(indent_pt)
    if align is not None: p.alignment = align
    if text: _rf(p.add_run(text), cn, size, bold)
    return p

def PAGEBREAK(doc):
    p = doc.add_paragraph(); p.paragraph_format.line_spacing = 1.5
    _rf(p.add_run(), CN_BODY, 12).add_break(WD_BREAK.PAGE)
    return p

def H1(doc, t): return P(doc, t, size=16, cn=CN_HEAD, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, sa=6, sb=6)
def H2(doc, t): return P(doc, t, size=14, cn=CN_HEAD, bold=True, sa=3, sb=6)
def H3(doc, t): return P(doc, t, size=11, cn=CN_HEAD, bold=True, sa=3, sb=3)
def BODY(doc, t, indent=True):
    return P(doc, t, size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent_pt=24 if indent else 0)
def CAP(doc, t): return P(doc, t, size=10.5, cn=CN_BODY, align=WD_ALIGN_PARAGRAPH.CENTER, sa=3, sb=3)
def FIGURE(doc, path, w=13.0):
    if not os.path.exists(path):
        print("  [缺图]", path); return
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2); p.paragraph_format.line_spacing = 1.0
    p.add_run().add_picture(path, width=Cm(w))

def _grid(tbl, on=True):
    tblPr = tbl._tbl.tblPr
    old = tblPr.find(qn('w:tblBorders'))
    if old is not None: tblPr.remove(old)
    bd = OxmlElement('w:tblBorders')
    for edge in ('top','left','bottom','right','insideH','insideV'):
        e = OxmlElement('w:'+edge)
        e.set(qn('w:val'), 'single' if on else 'none')
        e.set(qn('w:sz'), '4' if on else '0'); e.set(qn('w:color'), '000000')
        bd.append(e)
    tblPr.append(bd)

def TABLE(doc, headers, rows, widths=None, fs=10.5):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER; _grid(t, True)
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]; c.text = ""
        p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
        _rf(p.add_run(str(h)), CN_HEAD, fs, True)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
            _rf(p.add_run(str(v)), CN_BODY, fs)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    return t

# ================================================================
doc = Document()
st = doc.styles['Normal']
st.font.name = EN; st.font.size = Pt(12)
st.element.rPr.rFonts.set(qn('w:eastAsia'), CN_BODY)
st.paragraph_format.line_spacing = 1.5

sec = doc.sections[0]
sec.page_width = Cm(21.0); sec.page_height = Cm(29.7)
sec.top_margin = Cm(2.54); sec.bottom_margin = Cm(2.54)
sec.left_margin = Cm(3.18); sec.right_margin = Cm(3.18)

# ---------------- 封面（自然流，无强制分页） ----------------
P(doc, ""); P(doc, "")
P(doc, "【此处放置四个 Logo：CPIPC / 中国研究生创新实践系列大赛 / HUAWEI / 校徽】",
  size=12, align=WD_ALIGN_PARAGRAPH.CENTER)
P(doc, ""); P(doc, "")
P(doc, "中国研究生创新实践系列大赛", size=22, cn=CN_HEAD, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
P(doc, "“华为杯”第二十三届中国研究生", size=22, cn=CN_HEAD, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
P(doc, "数学建模竞赛", size=22, cn=CN_HEAD, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
for _ in range(8): P(doc, "")
P(doc, "“华为杯”第二十三届中国研究生", size=18, cn=CN_HEAD, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
P(doc, "数学建模竞赛", size=18, cn=CN_HEAD, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
P(doc, "")
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.line_spacing = 1.5
_rf(p.add_run("题　目："), CN_HEAD, 14, True)
_rf(p.add_run("多源数据质量评价、广义标度律与算力约束下的资源配置优化"), CN_BODY, 14)
P(doc, "")

# ---------------- 摘要（紧跟封面，不强制分页） ----------------
P(doc, "摘　要：", size=16, cn=CN_HEAD, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, sb=6, sa=6)
BODY(doc, "本文围绕大规模语言模型预训练中的多源数据质量评价、广义标度律刻画与算力约束下的资源配置问题，"
          "以附件 A（数据价值）、附件 B（标度律）与附件 C（效率演进）的真实数据为基础，"
          "构建了“质量评价—规律刻画—优化决策”的三层递进模型体系，"
          "并采用轨迹分块 Bootstrap、参数扰动与蒙特卡洛模拟对各层结论的稳健性进行了系统检验。")
BODY(doc, "针对问题一，本文从多源语料的 22 个质量指标出发，构建了分组熵权综合评价模型，"
          "将语义相近的指标归入六组以抑制同类评分器重复计权，识别出七域质量排序为 "
          "arxiv＞book＞stackexchange＞commoncrawl＞c4＞wikipedia＞github；"
          "以平均并列秩定义冲突强度，在 90% 分位阈值下识别出强冲突记录 27,252 条（占比 10.00%），"
          "并采用加权中位数稳健聚合得到 S_star 评分；最后建立领域配比与验证损失之间的线性及二阶岭回归模型，"
          "二阶组合项在同尺度 1M 检验集上的 RMSE 显著低于线性岭回归"
          "（500 次配对 Bootstrap 的 RMSE 差 95% 条件区间为 [−0.0639, −0.0166]）。")
BODY(doc, "针对问题二，本文以 B1 真实训练日志为基础，采用 Huber 稳健损失与自编 L-BFGS 多初值优化，"
          "估计出经典 Chinchilla 型缩放律参数（E=1.689870，A_N=0.353956，A_D=1.240274，α=0.339995，β=0.279906），"
          "并按 run_id 分块 Bootstrap 200 次给出参数置信区间；"
          "在此基础上构造有效数据量式与乘性质量式两种广义形式，以 BIC 与 B7 留出误差为双准则择优，"
          "最终选定乘性质量式 L₂ = L_p[1+κ(1−Q)^μ]，其 BIC 为 −1983.14、B7 留出 R² 为 0.9760，"
          "均优于有效数据量式（BIC=−1735.75，R²=0.9363）；"
          "据此量化得到数据质量提升 0.1 在 10B 与 100B 参数规模下的等效参数倍数分别为 1.779 与 3.933。")
BODY(doc, "针对问题三，本文以问题二标度律为目标函数，在总算力预算约束下联合优化参数量 N、数据量 D 与数据质量 Q，"
          "解析求出注意力开销与训练开销相等的临界上下文长度，"
          "并采用变点检测与活跃约束集跃迁分析识别出成本结构的结构性转移点。")
BODY(doc, "综上，本文形成了从数据到模型、从模型到决策、从决策到验证的完整证据链，"
          "可为大规模预训练语料的筛选、配比设计与算力分配提供定量支持。")
p = doc.add_paragraph(); pf = p.paragraph_format
pf.first_line_indent = Pt(24); pf.line_spacing = 1.5
_rf(p.add_run("关键词："), CN_HEAD, 12, True)
_rf(p.add_run("质量评价　广义标度律　分组熵权　弹性分析　资源优化"), CN_BODY, 12)

# ---------------- 分页 → 目录 ----------------
PAGEBREAK(doc)
P(doc, "目　录", size=16, cn=CN_HEAD, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, sb=12)
toc = [
    ("一、问题重述","3"),("1.1 问题背景","3"),("1.2 问题提出","3"),
    ("二、问题分析","3"),
    ("三、模型假设与符号说明","3"),("3.1 模型基本假设","3"),("3.2 符号说明","3"),
    ("四、数据预处理","3"),("4.1 指标选取","3"),("4.2 数据清洗","3"),
    ("五、模型建立与求解","3"),
    ("5.1 问题一模型建立与求解","3"),("5.1.1 问题一求解思路","3"),
    ("5.1.2 问题一模型建立","4"),("5.1.3 问题一模型求解与分析","4"),
    ("5.2 问题二模型建立与求解","4"),("5.2.1 问题二求解思路","4"),
    ("5.2.2 问题二模型建立","4"),("5.2.3 问题二模型求解与分析","4"),
    ("5.3 问题三模型建立与求解","4"),("5.3.1 问题三求解思路","4"),
    ("5.3.2 问题三模型建立","4"),("5.3.3 问题三模型求解与分析","4"),
    ("六、模型分析检验","4"),("6.1 灵敏度分析","4"),("6.2 误差分析","4"),
    ("七、模型评价与推广","5"),("7.1 模型的优点","5"),("7.2 模型的不足","5"),("7.3 模型的推广","5"),
    ("参考文献","6"),("附录","7"),
]
for txt, pg in toc:
    p = doc.add_paragraph(); pf = p.paragraph_format
    pf.line_spacing = 1.5; pf.space_after = Pt(0)
    pf.tab_stops.add_tab_stop(Cm(14.6), WD_TAB_ALIGNMENT.RIGHT, leader=2)
    _rf(p.add_run(txt), CN_BODY, 12)
    _rf(p.add_run("\t" + pg), CN_BODY, 12)

# ================================================================
# 正文一到四章
# ================================================================
import gen_front
gen_front.build(doc, {
    'H1': H1, 'H2': H2, 'H3': H3, 'BODY': BODY, 'CAP': CAP,
    'TABLE': TABLE, 'P': P, 'PAGEBREAK': PAGEBREAK, 'FIGURE': FIGURE,
})

doc.save(OUT)
print("已生成:", OUT)
