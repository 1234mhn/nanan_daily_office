#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""严格按官方模板规格生成封面+摘要+目录+正文第一~四章"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

def setup_document():
    """初始化文档并设置页面"""
    doc = Document()

    # 设置页面：A4，边距精确匹配模板
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.17)
    section.right_margin = Cm(3.17)

    # 修改 Normal 样式：Times New Roman + 宋体 12pt，行距1.5倍
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    style._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

    pf = style.paragraph_format
    pf.line_spacing = 1.5
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)

    return doc

def add_run_with_font(paragraph, text, size_pt, bold=False, font_name='Times New Roman', east_asia='宋体'):
    """添加文本 run 并设置中西文字体"""
    run = paragraph.add_run(text)
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn('w:eastAsia'), east_asia)
    return run

# ========== 正文排版函数 ==========

EN = "Times New Roman"
CN_BODY = "宋体"
CN_HEAD = "黑体"

def _rf(run, cn, size, bold=False):
    """设置 run 的中西文字体"""
    run.font.name = EN
    rPr = run._element.get_or_add_rPr()
    rf = rPr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts')
        rPr.insert(0, rf)
    rf.set(qn('w:ascii'), EN)
    rf.set(qn('w:hAnsi'), EN)
    rf.set(qn('w:eastAsia'), cn)
    run.font.size = Pt(size)
    run.bold = bold
    return run

def P(doc, text="", size=12, cn=CN_BODY, bold=False, align=None,
      indent_pt=0, line=1.5, sa=0, sb=0):
    """通用段落函数"""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing = line
    pf.space_after = Pt(sa)
    pf.space_before = Pt(sb)
    if indent_pt:
        pf.first_line_indent = Pt(indent_pt)
    if align is not None:
        p.alignment = align
    if text:
        _rf(p.add_run(text), cn, size, bold)
    return p

def PAGEBREAK(doc):
    """分页符"""
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    _rf(p.add_run(), CN_BODY, 12).add_break(WD_BREAK.PAGE)
    return p

def H1(doc, t):
    """一级标题：三号（16pt）黑体 加粗 居中（官方模板规范）"""
    return P(doc, t, size=16, cn=CN_HEAD, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, sa=6, sb=6)

def H2(doc, t):
    """二级标题：四号（14pt）黑体 加粗 左对齐（官方模板规范）"""
    return P(doc, t, size=14, cn=CN_HEAD, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, sa=3, sb=6)

def H3(doc, t):
    """三级标题：11pt 黑体 加粗"""
    return P(doc, t, size=11, cn=CN_HEAD, bold=True, sa=3, sb=3)

def BODY(doc, t, indent=True):
    """正文：12pt 两端对齐 首行缩进24pt"""
    return P(doc, t, size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent_pt=24 if indent else 0)

def CAP(doc, t):
    """图表标题：10.5pt 居中"""
    return P(doc, t, size=10.5, cn=CN_BODY, align=WD_ALIGN_PARAGRAPH.CENTER, sa=3, sb=3)

def FIGURE(doc, path, width_cm=13.0):
    """插入居中图片"""
    import os
    if not os.path.exists(path):
        print("  [缺图]", path); return
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2); p.paragraph_format.line_spacing = 1.0
    p.add_run().add_picture(path, width=Cm(width_cm))

def _grid(tbl, on=True):
    """设置表格边框"""
    tblPr = tbl._tbl.tblPr
    old = tblPr.find(qn('w:tblBorders'))
    if old is not None:
        tblPr.remove(old)
    bd = OxmlElement('w:tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        e = OxmlElement('w:' + edge)
        e.set(qn('w:val'), 'single' if on else 'none')
        e.set(qn('w:sz'), '4' if on else '0')
        e.set(qn('w:color'), '000000')
        bd.append(e)
    tblPr.append(bd)

def TABLE(doc, headers, rows, widths=None, fs=10.5):
    """表格：Table Grid 样式 10.5pt"""
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    _grid(t, True)

    # 表头
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = ""
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        _rf(p.add_run(str(h)), CN_HEAD, fs, True)

    # 数据行
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            _rf(p.add_run(str(v)), CN_BODY, fs)

    # 设置列宽
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)

    return t

def _new_section(doc):
    """在文末插入「下一页」分节符"""
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    sectPr = OxmlElement('w:sectPr')
    t = OxmlElement('w:type'); t.set(qn('w:val'), 'nextPage')
    sectPr.append(t)
    pPr.append(sectPr)
    return p


def build_cover(doc):
    """生成封面（不加分页符，与摘要连续流）"""
    # 空段 ×1
    doc.add_paragraph()

    # Logo 提示行（居中，12pt 常规）
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run_with_font(p, '【此处放置四个 Logo：CPIPC / 中国研究生创新实践系列大赛 / HUAWEI / 校徽】', 12)

    # 空段 ×1
    doc.add_paragraph()

    # 三行大标题 22pt 加粗居中
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run_with_font(p, '中国研究生创新实践系列大赛', 22, bold=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run_with_font(p, '"华为杯"第二十三届中国研究生', 22, bold=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run_with_font(p, '数学建模竞赛', 22, bold=True)

    # 空段 ×3（压缩以容纳摘要同页）
    for _ in range(3):
        doc.add_paragraph()

    # 两行标题 18pt 加粗居中
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run_with_font(p, '"华为杯"第二十三届中国研究生', 18, bold=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run_with_font(p, '数学建模竞赛', 18, bold=True)

    # 空段 ×1
    doc.add_paragraph()

    # 题目行（居中，14pt 加粗 + 14pt 常规）
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run_with_font(p, '题　目：', 14, bold=True)
    add_run_with_font(p, '大语言模型训练的多源语料质量评价与标度律建模', 14, bold=False)

    # 空段 ×1
    doc.add_paragraph()

    # 封面信息表（学校 / 参赛队号 / 队员姓名，无边框）
    _cover_info_table(doc)


def _no_border_table(doc, rows, label):
    """无边框两列表（标签 + 填写位）"""
    t = doc.add_table(rows=len(rows), cols=2)
    t.style = 'Normal Table'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblPr = t._tbl.tblPr
    old = tblPr.find(qn('w:tblBorders')) if tblPr.find(qn('w:tblBorders')) is not None else None
    bd = OxmlElement('w:tblBorders')
    for edge in ('top','left','bottom','right','insideH','insideV'):
        e = OxmlElement('w:'+edge); e.set(qn('w:val'),'none'); e.set(qn('w:sz'),'0')
        bd.append(e)
    tblPr.append(bd)
    for i,(a,b) in enumerate(rows):
        for j,txt in enumerate((a,b)):
            c = t.rows[i].cells[j]; c.text = ""
            p = c.paragraphs[0]
            p.paragraph_format.line_spacing = 1.5
            p.paragraph_format.space_after = Pt(0)
            if j == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                add_run_with_font(p, txt, 14, bold=True)
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                add_run_with_font(p, txt, 14, bold=False)
        t.rows[i].cells[0].width = Cm(3.2)
        t.rows[i].cells[1].width = Cm(8.0)
    return t


def _cover_info_table(doc):
    """封面信息区：学校 / 参赛队号 / 队员姓名"""
    _no_border_table(doc, [('学　　校', '\u3000'), ('参赛队号', '\u3000')], None)
    _no_border_table(doc, [('队员姓名', '\u3000'), ('', '1.\u3000'), ('', '2.\u3000'), ('', '3.\u3000')], None)


def _add_footer_page(doc):
    """在指定节页脚居中插入 PAGE 域"""
    sec = doc.sections[-1]
    sec.footer.is_linked_to_previous = False
    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = fp.add_run()
    fld = OxmlElement('w:fldSimple')
    fld.set(qn('w:instr'), 'PAGE \\* MERGEFORMAT')
    r._element.addnext(fld)

def build_abstract(doc):
    """摘要（与封面同页连续排版，不加分页/分节符）"""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    add_run_with_font(p, '摘　要：', 16, bold=True)

    # 摘要正文 12pt 两端对齐 首行缩进24pt
    abstract_text = [
        "随着大规模语言模型参数规模与训练数据规模的持续增长，数据质量与领域配比已成为决定模型性能的关键因素。传统的标度律主要关注参数规模与数据量，但无法区分数据质量、领域组成与模型性能之间的独立作用。本文基于附件 A 的多源语料质量指标与领域配比数据、附件 B 的标度律实验记录以及附件 C 的模型效率配置，建立从数据质量评价到广义标度律、从标度律到资源配置优化的完整建模框架。",

        "针对问题一，本文构建基于熵权法的多指标质量评价体系，采用秩尺度变换与 Huber 损失控制异常值，识别并标记质量评价冲突记录。在此基础上，建立领域配比与验证损失之间的二次校准模型，量化了配比偏离参考方案的损失代价。实验表明，代码与公式领域的质量评分显著高于自然语言领域，配比优化可使损失下降 0.012 nat/token。",

        "针对问题二，本文将问题一的质量评分引入经典标度律，提出两种候选广义标度律形式：加性质量惩罚与乘性质量系数。通过 AIC、BIC 与留出误差比较，确定乘性形式为最优模型。该模型在 Q=1 时自动退化为经典标度律，参数规模弹性为 −0.146、数据量弹性为 −0.084、质量弹性为 −0.519，表明数据质量提升的边际效用显著高于规模扩张。进一步分析表明，质量从 0.5 提升至 1.0 的效果等价于参数规模扩大 2.8 倍。",

        "针对问题三，本文以问题二的广义标度律为目标函数，在算力预算约束下联合优化参数规模、数据量与数据质量。通过梯度投影法求解非线性规划问题，发现最优策略呈现两阶段结构：预算较低时优先提升质量，预算较高时转向扩大参数规模。在 1021、1022、1023 FLOPs 三个预算水平下，给出了详细的资源配置方案与相应的损失预测值。",

        "综上，本文形成了从数据到模型、从模型到决策、从决策到验证的完整证据链，可为大规模语言模型训练中的数据采集与资源配置提供理论依据与实用方法。"
    ]

    for text in abstract_text:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pf = p.paragraph_format
        pf.first_line_indent = Pt(24)  # 首行缩进 2 字符
        add_run_with_font(p, text, 12)

    # 关键词行（12pt 加粗 + 常规，全角空格分隔）
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Pt(24)
    add_run_with_font(p, '关键词：', 12, bold=True)
    add_run_with_font(p, '大语言模型　数据质量评价　标度律　多目标优化　算力配置', 12)

    # —— 摘要与封面同页；在摘要结束后插入分节符（下一页为新节，页码从此起算） ——
    _new_section(doc)

def build_toc(doc):
    """生成目录（前面加分页符）"""
    # 在目录前加分页符
    doc.add_page_break()

    # 目录标题 16pt 加粗居中（官方模板规范）
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run_with_font(p, '目　录', 16, bold=True)

    # 目录条目：12pt，右对齐制表位 + 点线引导符
    # 制表位位置约 14.6cm（从左边距起算）
    toc_entries = [
        ('一、问题重述', True, [
            ('1.1 问题背景', False),
            ('1.2 问题提出', False),
        ]),
        ('二、问题分析', True, []),
        ('三、模型假设与符号说明', True, [
            ('3.1 模型基本假设', False),
            ('3.2 符号说明', False),
        ]),
        ('四、数据预处理', True, [
            ('4.1 指标选取', False),
            ('4.2 数据清洗', False),
        ]),
        ('五、模型建立与求解', True, [
            ('5.1 问题一模型建立与求解', False),
            ('5.2 问题二模型建立与求解', False),
            ('5.3 问题三模型建立与求解', False),
        ]),
        ('六、模型分析检验', True, [
            ('6.1 灵敏度分析', False),
            ('6.2 误差分析', False),
        ]),
        ('七、模型评价与推广', True, [
            ('7.1 模型优点', False),
            ('7.2 模型不足', False),
            ('7.3 模型推广', False),
        ]),
        ('参考文献', True, []),
        ('附录', True, []),
    ]

    page_num = 1  # 摘要起始页码
    for title, is_h1, children in toc_entries:
        p = doc.add_paragraph()
        pf = p.paragraph_format

        # 设置右对齐制表位 + 点线引导符（14.6cm）
        tab_stops = pf.tab_stops
        tab_stop = tab_stops.add_tab_stop(Cm(14.6), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)

        # 标题文本
        run = p.add_run(title)
        run.font.size = Pt(12)
        run.font.bold = is_h1
        run.font.name = 'Times New Roman'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

        # 制表符 + 页码
        p.add_run('\t')
        run = p.add_run(str(page_num))
        run.font.size = Pt(12)
        run.font.bold = is_h1
        run.font.name = 'Times New Roman'

        # 子条目（缩进）
        for child_title, _ in children:
            p = doc.add_paragraph()
            pf = p.paragraph_format
            tab_stops = pf.tab_stops
            tab_stop = tab_stops.add_tab_stop(Cm(14.6), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)

            pf.left_indent = Cm(0.74)   # 二级标题缩进（目录层级）
            run = p.add_run(child_title)
            run.font.size = Pt(12)
            run.font.bold = False
            run.font.name = 'Times New Roman'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

            p.add_run('\t')
            run = p.add_run(str(page_num))
            run.font.size = Pt(12)
            run.font.name = 'Times New Roman'

def build_chapter_1_to_4(doc):
    """生成正文第一~四章"""
    # 分页后开始正文
    PAGEBREAK(doc)

    # ========== 一、问题重述 ==========
    H1(doc, "一、问题重述")
    H2(doc, "1.1 问题背景")
    BODY(doc, "随着大规模语言模型参数规模与训练数据规模的持续增长，数据本身的构成与质量已成为决定模型性能的关键因素。"
              "传统的最小化验证交叉熵损失主要关注参数规模 N 与训练数据量 D，但无法区分数据数量、数据质量与领域组成三者的独立作用。"
              "与此同时，多源语料在采集过程中往往来自不同领域，存在质量参差不齐、指标相互冲突、配比难以优化等现实问题。"
              "如何在保持模型可解释性的前提下，将数据质量评分与领域配比纳入统一的预测与决策框架，"
              "并进一步在有限的算力预算下给出最优资源配置，是当前大规模预训练实践中亟待解决的核心矛盾。")
    BODY(doc, "附件 A 提供了多源语料的质量评分与领域配比实验数据，附件 B 提供了不同模型族与数据规模下的标度律实验记录，"
              "附件 C 提供了模型效率演进与上下文长度的相关配置。三组附件共同构成了从数据到规律、从规律到决策的完整信息链条。")
    H2(doc, "1.2 问题提出")
    BODY(doc, "问题一：基于附件 A 提供的多源语料质量指标与领域配比数据，建立数据质量评价体系，"
              "识别并消解不同指标之间的质量评价冲突，并建立领域配比与验证损失之间的定量关系模型。")
    BODY(doc, "问题二：基于附件 A 的质量评价结果与附件 B 的标度律实验数据，"
              "构建同时包含参数规模 N、数据量 D、数据质量 Q 与领域配比 p 的广义标度律，"
              "分析各因素的边际效用与弹性，并推导质量提升与规模扩张之间的可替代条件。")
    BODY(doc, "问题三：在给定总算力预算的约束下，联合优化参数量 N、数据量 D 与数据质量 Q，"
              "考察预算跨量级变化时最优策略是否发生结构性转移，并给出相应的资源配置方案。")

    # ========== 二、问题分析 ==========
    H1(doc, "二、问题分析")
    BODY(doc, "三问之间构成递进关系：问题一从数据侧出发，输出质量评分与配比关系；"
              "问题二将问题一的输出作为输入，刻画质量与配比对损失的影响规律；"
              "问题三以问题二的标度律为目标函数，在算力约束下给出最优决策。")
    BODY(doc, "问题一属于评价与回归问题。其切入角度是先建立可解释的质量指标体系，再用稳健统计方法处理指标冲突，"
              "最后建立配比与损失的定量模型。需要的数据包括 A1—A3 的多源语料质量指标、A4—A5 的配方与损失表，"
              "以及 A6—A15 的不同尺度检验表。预期产出为域级质量评分、冲突标记以及配比系数，为问题二提供 Q 与 p 的取值依据。")
    BODY(doc, "问题二属于规律拟合与模型比较问题。其关键难点在于如何将质量 Q 与配比 p 合理地引入经典标度律，"
              "同时保证模型在 Q 取理想值时能够退化为经典形式。本文通过构造两种候选形式并以 AIC、BIC 与留出误差择优来解决这一问题。")
    BODY(doc, "问题三属于带约束的非线性优化问题。其目标函数为问题二建立的广义标度律，"
              "约束为包含基础训练开销、质量提升开销与长文本注意力开销的算力预算，"
              "决策变量为参数规模、数据量与数据质量。该问题的核心在于识别最优解随预算变化的定性结构。")

    # ========== 三、模型假设与符号说明 ==========
    H1(doc, "三、模型假设与符号说明")
    H2(doc, "3.1 模型基本假设")
    BODY(doc, "本文的模型假设针对现实中可能存在的复杂状况与各类误差影响而设立，不为简化计算而假设掉题目给出的关键条件，具体如下：")
    for a in [
        "(1) 同一模型系列的验证损失可分解为不可约损失、有限参数损失与有限数据损失三部分，该假设把训练轨迹映射为可估计的二项幂律形式。",
        "(2) 质量得分 Q 越大表示数据质量越高，Q=1 表示无额外质量惩罚的基准水平，该假设保证广义形式在理想质量下退化为经典标度律。",
        "(3) 领域配比的影响在参考配比 p_ref 邻域内可由二次函数局部校准，即 m(p)=exp[−ηΔ_p(p)]，该处理把较低的配比损失映射为较大的有效数据量。",
        "(4) 同一 run_id 内的检查点具有轨迹相关性，因此统计推断以完整轨迹为抽样块，不把全部检查点视为独立重复观测。",
        "(5) 跨模型族允许绝对损失存在族间截距差异，跨族数据采用族内留一偏移校准判断曲线形状，不修改主模型的尺度参数。",
        "(6) 半合成质量实验数据分别估计而不直接合并，当参数触及边界或拟合方向相反时，将其解释为适用性失败而非强行平均。",
        "(7) 不主观删除正值离群记录，采用 Huber 损失降低异常残差的影响；非正数据量记录按缺失处理。",
        "(8) 各领域质量指标采用“自然语言可读性及知识表达”的方向假设，并以去除文本形态组作为敏感性对照，对代码、公式与表格不作绝对优劣判断。",
    ]:
        BODY(doc, a)

    H2(doc, "3.2 符号说明")
    BODY(doc, "本文使用的主要符号及其含义如表 1 所示。")
    CAP(doc, "表1　符号说明")
    TABLE(doc, ["符号", "含义", "单位"], [
        ["N", "模型参数规模", "十亿参数"],
        ["D", "累计训练数据规模", "十亿词元"],
        ["Q", "数据质量得分", "无量纲"],
        ["p", "领域配比向量", "无量纲"],
        ["L、L̂", "观测损失与预测损失", "nat/token"],
        ["E", "不可约损失", "nat/token"],
        ["A_N、A_D", "参数项与数据项系数", "nat/token"],
        ["α、β", "参数项与数据项指数", "无量纲"],
        ["Δ_p(p)", "相对参考配比的配比损失差", "nat/token"],
        ["η", "配比—有效数据量校准系数", "token/nat"],
        ["m(p)", "领域配比有效性乘子", "无量纲"],
        ["D_eff", "质量与配比修正后的有效数据量", "十亿词元"],
        ["θ_Q", "质量对有效数据量的指数", "无量纲"],
        ["G、γ", "低质量惩罚系数与指数", "nat/token，无量纲"],
        ["κ、μ", "乘性质量系数与指数", "无量纲"],
        ["ε_N、ε_D、ε_Q", "损失对 N、D、Q 的弹性", "无量纲"],
        ["C", "训练计算量", "10²¹ FLOPs"],
        ["MRC", "单位算力边际损失下降", "每 10²¹ FLOPs"],
        ["δ_Q", "质量提升量", "无量纲"],
        ["N_equiv", "质量提升的等效参数规模", "十亿参数"],
        ["S_s", "单条记录的分组熵权综合质量评分", "无量纲"],
        ["S_d", "域内记录平均质量评分", "无量纲"],
        ["S_star", "秩尺度稳健评分", "无量纲"],
        ["w_g", "组间熵权", "无量纲"],
        ["c_s", "单条记录的冲突强度", "无量纲"],
        ["δ", "冲突判定阈值（90% 分位）", "无量纲"],
    ], widths=[3.5, 7.5, 3.5], fs=10.5)

    # ========== 四、数据预处理 ==========
    H1(doc, "四、数据预处理")
    H2(doc, "4.1 指标选取")
    BODY(doc, "本文根据问题需要共选取 22 个质量指标，涵盖内容教育价值、语言流畅度、广告含量、参考域相似性、"
              "重复与字符结构以及文本形态六个方面。各指标的数据来源为附件 A1—A3 的原始记录。"
              "各指标的归一化前处理规则与处理后方向如表 2 所示。")
    CAP(doc, "表2　全部 22 个指标的处理规则")
    TABLE(doc, ["字段", "归一化前处理", "处理后方向"], [
        ["fineweb_edu", "列表首项", "正"],
        ["ad_en、fluency_en", "第二项减第一项", "正"],
        ["modernbert 四项", "softmax 期望等级", "正"],
        ["qurater", "四项评分算术平均", "正"],
        ["dsir_books、dsir_math、dsir_wiki", "ln(1−x)", "反"],
        ["rps_doc_word_count、num_sentences", "ln(1+x)", "正"],
        ["rps_doc_unigram_entropy", "原值", "正"],
        ["rps_doc_frac_unique_words", "原值", "正"],
        ["rps_doc_frac_no_alph_words", "原值", "反"],
        ["rps_doc_frac_chars_top_2gram、top_3gram", "原值", "反"],
        ["rps_lines_uppercase_letter_fraction", "原值", "反"],
        ["rps_lines_numerical_chars_fraction", "原值", "反"],
        ["rps_lines_ending_with_terminal_punctution_mark", "原值", "正"],
        ["rps_doc_mean_word_length", "原值", "反"],
    ], widths=[6.5, 5.0, 3.0], fs=10.0)
    BODY(doc, "四个 modernbert 字段为 0—5 级分类输出，以 softmax 期望等级保留连续信息，计算时先减去最大 logit 以避免溢出；"
              "qurater 四维分别描述文风、知识门槛、事实知识与教育价值，采用四项原始评分的等权均值，属于建模选择而非原题指定权重。"
              "计数指标取 ln(1+x)，三个 DSIR 字段在本数据中全部非正，取 ln(1−x) 后反向归一化，以保留原始 DSIR 越大越优的相对方向。")
    BODY(doc, "将正向指标缩放为 V=(X−min)/(max−min)，反向指标取 1−V；常量列设为 0.5 并将熵权置零。"
              "重尾变换后按域中位数填补非有限值，实际缺失为 modernbert_reasoning 13 项、modernbert_professionalism 6 项。")

    H2(doc, "4.2 数据清洗")
    BODY(doc, "附件 A1—A3 共 272,505 条记录。按“领域＋id”识别出 11,419 条重复记录，唯一文档数为 261,086，跨域重复率为 4.19%。"
              "主评分保留并计算全部记录，另做去重重估敏感性分析；扩展复检排除与 A1 重叠的记录，剩余 arxiv 16,104 条、github 193,752 条。")
    BODY(doc, "配方表与损失表按 index 一一连接，共 1,214 组，其中实测表 1,088 组、外推表 126 组。"
              "所有配比均非负，训练表原始行和范围为 0.996—1.003，采用逐行除以行和恢复单纯形约束，保留原有零比例。")
    BODY(doc, "在样本划分上，B7 以 B6 未出现的 experiment_id 形成 90 点留出集；"
              "B1 按 run_id 分组实施 200 次轨迹 Bootstrap，广义质量项按 (N,D) 单元实施 120 次分块 Bootstrap；参数规模留一验证共 8 轮。"
              "模型比较的岭回归超参数仅在 512 组训练配方内进行相同划分的 5 折验证，检验集不参与超参数选择。")

if __name__ == '__main__':
    doc = setup_document()
    build_cover(doc)
    build_abstract(doc)
    build_toc(doc)
    PAGEBREAK(doc)
    build_chapter_1_to_4(doc)

    _L = {'H1':H1,'H2':H2,'H3':H3,'BODY':BODY,'CAP':CAP,'TABLE':TABLE,
          'P':P,'PAGEBREAK':PAGEBREAK,'FIGURE':FIGURE}
    _L['FIG_DIR'] = '/root/.openclaw/workspace/huawei2026_F/paper/figures'
    import gen_51
    gen_51.build_51(doc, _L)

    # 封面节（第0节）不编页码；从第1节（摘要所在节）起页脚居中自动编号
    _add_footer_page(doc)

    output_path = 'docx/F题_论文.docx'
    doc.save(output_path)
    print(f'✅ 已生成：{output_path}')
