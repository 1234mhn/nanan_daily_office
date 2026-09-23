# -*- coding: utf-8 -*-
"""F题论文生成 —— 主脚本（前半部分：封面/摘要/目录/一~四章 + 5.1 + 5.2）"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from genlib import *
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.section import WD_SECTION

doc = Document()

# ============ 页面设置：A4，常规页边距 ============
sec = doc.sections[0]
sec.page_width = Cm(21.0)
sec.page_height = Cm(29.7)
sec.top_margin = Cm(2.54)
sec.bottom_margin = Cm(2.54)
sec.left_margin = Cm(3.18)
sec.right_margin = Cm(3.18)

# ============ 封面（无页码） ============
para(doc, "【此处放置四个 Logo：CPIPC / 中国研究生创新实践系列大赛 / HUAWEI / 校徽】",
     size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)
para(doc, "", space_after=6)
para(doc, "中国研究生创新实践系列大赛", size=16, cn=HEI, en=HEI, bold=True,
     align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
para(doc, "“华为杯”第二十三届中国研究生", size=16, cn=HEI, en=HEI, bold=True,
     align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
para(doc, "数学建模竞赛", size=16, cn=HEI, en=HEI, bold=True,
     align=WD_ALIGN_PARAGRAPH.CENTER, space_after=24)

# 信息表
info = doc.add_table(rows=3, cols=2)
info.style = 'Table Grid'
info.alignment = WD_TABLE_ALIGNMENT.CENTER
labels = ["学　　校", "参赛队号", "队员姓名"]
for i, lab in enumerate(labels):
    c0, c1 = info.rows[i].cells
    c0.text = ""
    p = c0.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(lab); set_run_font(r, HEI, HEI, 12, True)
    c1.text = ""
    p = c1.paragraphs[0]
    r = p.add_run("　"); set_run_font(r, SONG, TIMES, 12)
    c0.width = Cm(4); c1.width = Cm(9)

para(doc, "", space_after=18)
para(doc, "“华为杯”第二十三届中国研究生", size=16, cn=HEI, en=HEI, bold=True,
     align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
para(doc, "数学建模竞赛", size=16, cn=HEI, en=HEI, bold=True,
     align=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)
para(doc, "题　目：多源数据质量评价、广义标度律与算力约束下的资源配置优化",
     size=14, cn=HEI, en=HEI, bold=True,
     align=WD_ALIGN_PARAGRAPH.CENTER, space_after=24)

# ============ 摘要页（页码从此开始为1） ============
doc.add_page_break()
para(doc, "摘　要", size=14, cn=HEI, en=HEI, bold=True,
     align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)

body(doc, "本文围绕大规模语言模型预训练中的多源数据质量评价、广义标度律刻画与算力约束下的资源配置问题，"
          "以附件 A（数据价值）、附件 B（标度律）与附件 C（效率演进）的真实数据为基础，"
          "构建了“质量评价—规律刻画—优化决策”的三层递进模型体系，"
          "并采用轨迹分块 Bootstrap、参数扰动与蒙特卡洛模拟对各层结论的稳健性进行了系统检验。")

body(doc, "针对问题一，本文从多源语料的 22 个质量指标出发，构建了分组熵权综合评价模型，"
          "将语义相近的指标归入六组以抑制同类评分器重复计权，识别出七域质量排序为 "
          "arxiv＞book＞stackexchange＞commoncrawl＞c4＞wikipedia＞github；"
          "进一步以平均并列秩定义冲突强度，在 90% 分位阈值下识别出强冲突记录 27,252 条，"
          "占比 10.00%，并采用加权中位数稳健聚合得到 S_star 评分；"
          "最后建立领域配比与验证损失之间的线性及二阶岭回归模型，"
          "二阶组合项在同尺度 1M 检验集上的 RMSE 显著低于线性岭回归"
          "（500 次配对 Bootstrap 的 RMSE 差 95% 条件区间为 [−0.0639, −0.0166]）。")

body(doc, "针对问题二，本文以 B1 真实训练日志为基础，采用 Huber 稳健损失与自编 L-BFGS 多初值优化，"
          "估计出经典 Chinchilla 型缩放律参数（E=1.689870，A_N=0.353956，A_D=1.240274，"
          "α=0.339995，β=0.279906），并按 run_id 分块 Bootstrap 200 次给出参数置信区间；"
          "在此基础上构造有效数据量式与乘性质量式两种广义形式，"
          "以 BIC 与 B7 留出误差为双准则择优，最终选定乘性质量式 "
          "L₂ = L_p[1+κ(1−Q)^μ]，其 BIC 为 −1983.14、B7 留出 R² 为 0.9760，"
          "均优于有效数据量式（BIC=−1735.75，R²=0.9363）。"
          "据此量化得到数据质量提升 0.1 在 10B 与 100B 参数规模下的等效参数倍数分别为 1.779 与 3.933，"
          "并给出单位算力边际收益的递减规律。")

body(doc, "针对问题三，本文以问题二标度律为目标函数，在总算力预算约束下联合优化参数量 N、数据量 D 与数据质量 Q，"
          "解析求出注意力开销与训练开销相等的临界上下文长度，"
          "并采用 PELT 变点检测与活跃约束集跃迁分析识别出成本结构的结构性转移点。")

body(doc, "综上，本文形成了从数据到模型、从模型到决策、从决策到验证的完整证据链，"
          "可为大规模预训练语料的筛选、配比设计与算力分配提供定量支持。")

para(doc, "", space_after=6)
p = doc.add_paragraph()
r = p.add_run("关键词：")
set_run_font(r, HEI, HEI, 12, True)
r2 = p.add_run("质量评价　广义标度律　分组熵权　弹性分析　资源优化")
set_run_font(r2, SONG, TIMES, 12)

# ============ 目录 ============
doc.add_page_break()
para(doc, "目　录", size=14, cn=HEI, en=HEI, bold=True,
     align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)
toc = [
    ("一、问题重述", 0), ("1.1 问题背景", 1), ("1.2 问题提出", 1),
    ("二、问题分析", 0),
    ("三、模型假设与符号说明", 0), ("3.1 模型基本假设", 1), ("3.2 符号说明", 1),
    ("四、数据预处理", 0), ("4.1 指标选取", 1), ("4.2 数据清洗", 1),
    ("五、模型建立与求解", 0),
    ("5.1 问题一模型建立与求解", 1),
    ("5.1.1 问题一求解思路", 2), ("5.1.2 问题一模型建立", 2), ("5.1.3 问题一模型求解与分析", 2),
    ("5.2 问题二模型建立与求解", 1),
    ("5.2.1 问题二求解思路", 2), ("5.2.2 问题二模型建立", 2), ("5.2.3 问题二模型求解与分析", 2),
    ("5.3 问题三模型建立与求解", 1),
    ("5.3.1 问题三求解思路", 2), ("5.3.2 问题三模型建立", 2), ("5.3.3 问题三模型求解与分析", 2),
    ("六、模型分析检验", 0), ("6.1 灵敏度分析", 1), ("6.2 误差分析", 1),
    ("七、模型评价与推广", 0), ("7.1 模型的优点", 1), ("7.2 模型的不足", 1), ("7.3 模型的推广", 1),
    ("参考文献", 0), ("附录", 0),
]
for txt, lvl in toc:
    para(doc, txt, size=12, cn=SONG, en=TIMES, bold=(lvl == 0),
         indent_chars=0, space_after=0)

doc.save(OUT)
print("已生成:", OUT)
