#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数学建模竞赛论文机械扫描脚本

用途：从 PDF 中提取客观指标，供人工审核时核对。脚本只提供待核项，
不替代人工判断，所有结论均需在审核报告中复核。

用法：
    python scan_paper.py <paper.pdf> [--json out.json] [--text out.txt]

依赖：pypdf 或 pdfplumber（安装其一即可）
    pip install pypdf pdfplumber
"""

import argparse
import json
import re
import subprocess
import sys
from collections import OrderedDict, defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------- 文本提取

def extract_with_pypdf(path, password=""):
    try:
        from pypdf import PdfReader
    except ImportError:
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            return None
    try:
        reader = PdfReader(path)
        if reader.is_encrypted:
            try:
                reader.decrypt(password)
            except Exception:
                return None
        return [page.extract_text() or "" for page in reader.pages]
    except Exception:
        return None


def extract_with_pdfplumber(path, password=""):
    try:
        import pdfplumber
    except ImportError:
        return None
    try:
        pages = []
        with pdfplumber.open(path, password=password or None) as pdf:
            for page in pdf.pages:
                pages.append(page.extract_text() or "")
        return pages
    except Exception:
        return None


def extract_with_pdftotext(path):
    try:
        raw = subprocess.run(
            ["pdftotext", "-enc", "UTF-8", "-layout", path, "-"],
            capture_output=True, check=True, timeout=120,
        ).stdout
        text = raw.decode("utf-8", errors="replace")
    except Exception:
        return None
    return text.split("\f")


def extract_docx(path):
    """按显式分页符切分 docx 为近似页。docx 为流式格式，页数为近似值。"""
    try:
        import docx
        from docx.oxml.ns import qn
        from docx.text.paragraph import Paragraph
        from docx.table import Table
    except ImportError:
        return None
    try:
        d = docx.Document(path)
    except Exception:
        return None

    pages, buf = [], []

    def flush():
        if buf:
            pages.append("\n".join(buf))
            del buf[:]

    body = d.element.body
    for child in body.iterchildren():
        tag = child.tag.split("}")[-1]
        if tag == "p":
            p = Paragraph(child, d)
            text = p.text.strip()
            if text:
                buf.append(text)
            if any(b.get(qn("w:type")) == "page" for b in child.findall(".//" + qn("w:br"))):
                flush()
        elif tag == "tbl":
            try:
                t = Table(child, d)
                for row in t.rows:
                    buf.append(" | ".join(c.text.strip() for c in row.cells))
            except Exception:
                pass
    flush()
    return pages or [""]


def docx_headers_footers(path):
    """提取 docx 各节的页眉页脚文本，用于国赛禁页眉检查。"""
    try:
        import docx
    except ImportError:
        return None
    try:
        d = docx.Document(path)
    except Exception:
        return None
    out = []
    for i, sec in enumerate(d.sections, start=1):
        item = {"section": i}
        for part in ("header", "footer"):
            obj = getattr(sec, part)
            try:
                texts = [p.text.strip() for p in obj.paragraphs if p.text.strip()]
                item[part] = texts
            except Exception:
                item[part] = []
        out.append(item)
    return out


def extract_pages(path, password=""):
    if path.lower().endswith((".docx", ".doc")):
        pages = extract_docx(path)
        if pages:
            return pages, "python-docx"
        return None, None
    pages = extract_with_pypdf(path, password)
    if pages:
        return pages, "pypdf"
    pages = extract_with_pdfplumber(path, password)
    if pages:
        return pages, "pdfplumber"
    pages = extract_with_pdftotext(path)
    if pages:
        return pages, "pdftotext"
    return None, None


# ---------------------------------------------------------------- 基础分析

CJK = re.compile(r"[\u4e00-\u9fff]")


def language_of(texts):
    cjk = sum(len(CJK.findall(t)) for t in texts)
    latin = sum(len(re.findall(r"[A-Za-z]", t)) for t in texts)
    if cjk == 0 and latin == 0:
        return "无文本层（疑似扫描版）", 0, 0
    ratio = cjk / (cjk + latin)
    if ratio > 0.6:
        return "中文为主", cjk, latin
    if ratio < 0.2:
        return "英文为主", cjk, latin
    return "中英混排", cjk, latin


TEAM_HEADER = re.compile(r"Team\s*#?\s*(\d{5,8})\s*,?\s*Page\s*(\d+)\s*of\s*(\d+)", re.I)
TEAM_CN = re.compile(r"Team\s*#?\s*(\d{5,8})", re.I)
CONTROL_ONLY = re.compile(r"\b\d{7}\b")

PROMISE_CN = re.compile(r"我们仔细阅读了|郑重承诺|竞赛规则")
NUMBER_PAGE_CN = re.compile(r"赛区评阅编号|全国统一编号|全国评阅编号")
SUMMARY_SHEET = re.compile(r"Summary\s*Sheet", re.I)
AI_REPORT = re.compile(r"Report\s*on\s*Use\s*of\s*AI", re.I)
TOC_MARK = re.compile(r"^\s*(Contents|Table\s*of\s*Contents|目\s*录)\s*$", re.M)

IDENTITY_PATTERNS = OrderedDict([
    ("中文高校与院系", re.compile(r"[\u4e00-\u9fff]{2,}(大学|学院|学校|校区|附属中学)")),
    ("中文身份词", re.compile(r"(指导教师|指导老师|参赛队员|队员姓名|学号|班级|专业班级|致谢|感谢)")),
    ("英文机构", re.compile(r"\b(University|College|Institute\s+of\s+Technology|School\s+of)\b", re.I)),
    ("英文身份词", re.compile(r"\b(Advisor|Instructor|Professor|Student\s+ID|Acknowledg\w*)\b", re.I)),
    ("邮箱地址", re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")),
    ("本地路径", re.compile(r"[A-Za-z]:\\Users\\|/home/[\w.-]+/|/Users/[\w.-]+/")),
    ("网址正文混入", re.compile(r"https?://\S+")),
])

FIG_PATTERNS = [
    ("图", re.compile(r"图\s*(\d+(?:[-.]\d+)?)")),
    ("表", re.compile(r"(?<!图)表\s*(\d+(?:[-.]\d+)?)")),
    ("Figure", re.compile(r"\bFigure\s*(\d+(?:[-.]\d+)?)", re.I)),
    ("Table", re.compile(r"\bTable\s*(\d+(?:[-.]\d+)?)", re.I)),
]

# 标题行：行首即为 图/表 + 编号，其后紧跟标题文字
CAPTION_PATTERNS = [
    ("图", re.compile(r"^\s*图\s*(\d+(?:[-.]\d+)?)\s*")),
    ("表", re.compile(r"^\s*表\s*(\d+(?:[-.]\d+)?)\s*")),
    ("Figure", re.compile(r"^\s*Figure\s*(\d+(?:[-.]\d+)?)\s*[:\-.]?\s*", re.I)),
    ("Table", re.compile(r"^\s*Table\s*(\d+(?:[-.]\d+)?)\s*[:\-.]?\s*", re.I)),
]

# 行首出现 图/表 编号但属于正文引用的典型措辞
CAPTION_STOPWORDS = re.compile(r"(可知|可见|给出|显示|列出|所示|如下|进行了|用于|表明|反映)")


def looks_like_caption(line, m):
    """区分标题行与恰好以 图N/表N 开头的正文句。"""
    tail = line[m.end():].strip()
    if len(tail) < 2:
        return False
    if re.search(r"[。；;.!！]$", line.strip()):
        return False
    if CAPTION_STOPWORDS.search(tail):
        return False
    return True

EQ_LINE_END = re.compile(r"\(\s*(\d+(?:[-.]\d+)?)\s*\)\s*$")
CITE = re.compile(r"\[(\d{1,3})\]")
CITE_RANGE = re.compile(r"\[(\d{1,3})\s*[-–,]\s*(\d{1,3})\]")
REF_ENTRY = re.compile(r"^\s*[\[［(]?\s*(\d{1,3})\s*[\]］).、]\s*[\S\u4e00-\u9fff]")
ISBN13 = re.compile(r"97[89][- ]?\d{1,5}[- ]?\d{1,7}[- ]?\d{1,6}[- ]?(\d)")
DOI = re.compile(r"\b10\.\d{4,9}/[^\s\"'<>]+", re.I)


def isbn13_valid(s):
    digits = [c for c in s if c.isdigit()]
    if len(digits) != 13:
        return None
    total = sum((1 if i % 2 == 0 else 3) * int(d) for i, d in enumerate(digits[:12]))
    check = (10 - total % 10) % 10
    return check == int(digits[12])


def analyze_captions_vs_refs(captions, refs):
    """captions / refs: list of (kind, label, page)。返回编号与引用一致性诊断。"""
    by_kind = defaultdict(lambda: {"captions": [], "refs": []})
    for kind, label, page in captions:
        by_kind[kind]["captions"].append((label, page))
    for kind, label, page in refs:
        by_kind[kind]["refs"].append((label, page))

    out = []
    for kind in sorted(by_kind):
        caps = by_kind[kind]["captions"]
        referenced = {lab for lab, _ in by_kind[kind]["refs"]}
        cap_labels = [lab for lab, _ in caps]

        seen, dup = set(), []
        for lab in cap_labels:
            if lab in seen:
                dup.append(lab)
            seen.add(lab)

        # 编号连续性。带分隔符时按章分组，否则视为全文连续编号
        missing = []
        if any(re.search(r"[-.]", lab) for lab in seen):
            groups = defaultdict(list)
            for lab in seen:
                chap, num = re.split(r"[-.]", lab)
                groups[chap].append(int(num))
            for chap in sorted(groups, key=lambda x: int(x)):
                for n in range(1, max(groups[chap]) + 1):
                    if n not in groups[chap]:
                        missing.append("%s-%d" % (chap, n))
        elif seen:
            nums = sorted(int(x) for x in seen)
            for n in range(1, max(nums) + 1):
                if n not in nums:
                    missing.append(str(n))

        out.append({
            "kind": kind,
            "caption_count": len(caps),
            "caption_labels": cap_labels,
            "duplicate_captions": sorted(set(dup)),
            "missing_in_sequence": missing,
            "cited_but_no_caption": sorted(referenced - seen),
            "caption_never_cited": sorted(seen - referenced),
            "caption_pages": [{"label": lab, "page": pg} for lab, pg in caps][:40],
        })
    return out


def analyze_sequences(matches):
    """matches: list of (kind, label, order)。返回每类的编号诊断。"""
    grouped = defaultdict(list)
    for kind, label, order in matches:
        if "." in label or "-" in label:
            sep = "-" if "-" in label else "."
            chap, num = label.split(sep)
            grouped[(kind, chap)].append((int(num), label, order))
        else:
            grouped[(kind, "")].append((int(label), label, order))
    report = []
    for (kind, chap), items in sorted(grouped.items()):
        nums = [n for n, _, _ in items]
        seen, dup = set(), []
        for n in nums:
            if n in seen:
                dup.append(n)
            seen.add(n)
        gaps = []
        if nums:
            for n in range(1, max(nums) + 1):
                if n not in seen:
                    gaps.append(n)
        out_of_order = [
            (items[i][1], items[i + 1][1])
            for i in range(len(items) - 1)
            if items[i][0] > items[i + 1][0]
        ]
        counts = defaultdict(int)
        for n, _, _ in items:
            counts[n] += 1
        single = sorted([n for n, c in counts.items() if c == 1])
        report.append({
            "kind": kind,
            "chapter": chap or "全文连续",
            "labels": [lab for _, lab, _ in items],
            "duplicates": sorted(set(dup)),
            "missing": gaps,
            "out_of_order": out_of_order[:20],
            "appears_once": single,
        })
    return report


def scan(path, password=""):
    pages, engine = extract_pages(path, password)
    result = {"file": path, "engine": engine}

    if not pages:
        result["error"] = "无法提取文本，请安装 pypdf 或 pdfplumber（PDF）或 python-docx（docx），或确认文件为文本型 PDF"
        return result

    if engine == "python-docx":
        result["page_source"] = "docx 近似页（按显式分页符切分，页数不可靠）"
        result["page_count_reliable"] = False
        hf = docx_headers_footers(path)
        if hf:
            result["docx_headers_footers"] = hf
    else:
        result["page_source"] = "PDF 物理页"
        result["page_count_reliable"] = True

    pages = [p for p in pages]
    result["page_count"] = len(pages)

    lang, cjk, latin = language_of(pages)
    result["language"] = {"verdict": lang, "cjk_chars": cjk, "latin_chars": latin}

    # 页眉页脚
    headers, footers = [], []
    for i, text in enumerate(pages):
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        headers.append({"page": i + 1, "first_line": lines[0][:120] if lines else ""})
        footers.append({"page": i + 1, "last_line": lines[-1][:120] if lines else ""})

    team_headers, missing_header_pages, mismatch_pages = [], [], []
    for i, text in enumerate(pages):
        m = TEAM_HEADER.search(text)
        if m:
            team_headers.append({"page": i + 1, "control": m.group(1),
                                 "page_no": int(m.group(2)), "page_total": int(m.group(3))})
        else:
            missing_header_pages.append(i + 1)
    for item in team_headers:
        if item["page_no"] != item["page"]:
            mismatch_pages.append({"page": item["page"], "reason": "页眉页码与实际页码不符"})
        if item["page_total"] != len(pages):
            mismatch_pages.append({"page": item["page"], "reason": "页眉声明总页数 %d 与实际 %d 不符" % (item["page_total"], len(pages))})
    result["mcm_header"] = {
        "found": len(team_headers),
        "missing_pages": missing_header_pages,
        "mismatch_pages": mismatch_pages,
        "control_numbers": sorted({t["control"] for t in team_headers}),
        "declared_total": sorted({t["page_total"] for t in team_headers}),
        "sample": team_headers[:3],
    }

    # 页数合规
    page_rules = []
    reliable = result.get("page_count_reliable", True)
    page_rules.append({
        "rule": "MCM/ICM 全部内容不超过 25 页",
        "actual": len(pages),
        "passed": (len(pages) <= 25) if reliable else None,
        "note": "若含 Report on Use of AI，不计入 25 页，须人工扣除后复核"
                + ("" if reliable else "；当前页数来自近似切分，须导出 PDF 后复核"),
    })
    page_rules.append({
        "rule": "CUMCM 正文控制在 20 页以内（附录不限）",
        "actual": len(pages),
        "passed": None,
        "note": "需人工划分正文与附录边界后判定",
    })
    result["page_rules"] = page_rules

    # 赛事信号
    full = "\n".join(pages)
    def page_of(pattern):
        out = []
        for i, text in enumerate(pages):
            if pattern.search(text):
                out.append(i + 1)
        return out

    result["signals"] = {
        "cumcm_promise_pages": page_of(PROMISE_CN),
        "cumcm_number_pages": page_of(NUMBER_PAGE_CN),
        "mcm_summary_sheet_pages": page_of(SUMMARY_SHEET),
        "ai_use_report_pages": page_of(AI_REPORT),
        "toc_pages": page_of(TOC_MARK),
        "abstract_pages": page_of(re.compile(r"摘\s*要|Abstract|Summary", re.I))[:10],
    }

    # 身份泄露（排除承诺书与编号专用页，该两页出现校名与签名属规范允许）
    # 若全文只切出一个文本块（如无分页符的 docx），无法定位前置页，则不做排除
    single_block = len(pages) <= 1
    promise_pages = set()
    for i, text in enumerate(pages):
        if PROMISE_CN.search(text) or NUMBER_PAGE_CN.search(text):
            promise_pages.add(i + 1)
    result["front_matter_pages"] = [] if single_block else sorted(promise_pages)
    result["front_matter_excluded"] = not single_block

    leaks = []
    for name, pat in IDENTITY_PATTERNS.items():
        hits = []
        for i, text in enumerate(pages):
            if not single_block and (i + 1) in promise_pages:
                continue
            for m in pat.finditer(text):
                s = max(0, m.start() - 30)
                hits.append({"page": i + 1, "snippet": text[s:m.end() + 30].replace("\n", " ")})
                if len(hits) >= 15:
                    break
            if len(hits) >= 15:
                break
        if hits:
            leaks.append({"type": name, "count": len(hits), "samples": hits[:8]})
    result["identity_leaks"] = leaks

    # 页眉检测：首页行在多页重复出现即疑似页眉
    first_lines = [h["first_line"] for h in headers if h["first_line"]]
    counter = defaultdict(int)
    for ln in first_lines:
        counter[ln] += 1
    repeated = [{"line": k, "pages": v} for k, v in counter.items() if v >= max(3, len(pages) // 3)]
    result["suspected_header"] = repeated

    # 赛事初判
    has_promise = bool(result["signals"]["cumcm_promise_pages"])
    has_number_page = bool(result["signals"]["cumcm_number_pages"])
    has_summary_sheet = bool(result["signals"]["mcm_summary_sheet_pages"])
    team_hit = len(team_headers)
    is_cn = "中文" in lang or "混排" in lang
    verdict, basis = [], []
    if has_promise and has_number_page and is_cn:
        verdict.append("CUMCM 全国大学生数学建模竞赛")
        basis.append("检出承诺书页与编号专用页且正文为中文")
    if has_summary_sheet or team_hit >= max(2, len(pages) // 2):
        verdict.append("MCM/ICM 美国大学生数学建模竞赛")
        basis.append("检出 Summary Sheet 或 Team # 页眉")
    if not verdict:
        verdict.append("未能自动判定，需人工确认")
        basis.append("未检出足够的赛事标识信号")
    result["contest_prediction"] = {"verdict": verdict, "basis": basis}

    # 图表：区分标题行（定义）与正文引用
    cap_by_kind = {kind: pat for kind, pat in CAPTION_PATTERNS}
    cap_all, ref_all = [], []
    for i, text in enumerate(pages):
        for line in text.splitlines():
            handled = False
            for kind, cap_pat in cap_by_kind.items():
                m = cap_pat.match(line)
                if m and looks_like_caption(line, m):
                    cap_all.append((kind, m.group(1), i + 1))
                    handled = True
                    break
            if handled:
                continue
            for kind, pat in FIG_PATTERNS:
                for m in pat.finditer(line):
                    ref_all.append((kind, m.group(1), i + 1))
    result["figure_table_numbering"] = analyze_captions_vs_refs(cap_all, ref_all)

    # 公式编号
    eq = []
    for i, text in enumerate(pages):
        for line in text.splitlines():
            m = EQ_LINE_END.search(line.strip())
            if m:
                eq.append((i + 1, m.group(1)))
    result["equation_numbering"] = {"count": len(eq), "items": eq[:80]}

    # 引用与文献表
    # 章节标题可能被排版成「参 考 文 献」，用去空白视图匹配
    nospace = [re.sub(r"\s+", "", p) for p in pages]
    ref_start = None
    for i in range(len(nospace) - 1, -1, -1):
        if re.search(r"(参考文献|References|ReferenceList|Bibliography)",
                     nospace[i], re.I):
            ref_start = i
            break
    cited = set()
    for text in pages:
        for m in CITE_RANGE.finditer(text):
            try:
                a, b = int(m.group(1)), int(m.group(2))
                if b >= a and b - a < 60:
                    cited.update(range(a, b + 1))
            except ValueError:
                pass
        for m in CITE.finditer(text):
            cited.add(int(m.group(1)))

    ref_entries = []
    if ref_start is not None:
        for j in range(ref_start, len(pages)):
            for line in pages[j].splitlines():
                m = REF_ENTRY.match(line)
                if m:
                    ref_entries.append({"number": int(m.group(1)), "page": j + 1,
                                        "text": line.strip()[:300]})
    ref_nums = {e["number"] for e in ref_entries}

    result["references"] = {
        "section_page": (ref_start + 1) if ref_start is not None else None,
        "entry_count": len(ref_entries),
        "entry_numbers": sorted(ref_nums),
        "cited_numbers": sorted(cited),
        "cited_not_listed": sorted(cited - ref_nums) if ref_nums else [],
        "listed_not_cited": sorted(ref_nums - cited) if ref_nums else [],
        "entries": ref_entries,
    }

    # DOI 与 ISBN
    dois,isbns = [], []
    for text in pages:
        for m in DOI.finditer(text):
            dois.append(m.group(0).rstrip(".,;)）"))
    for text in pages:
        for m in ISBN13.finditer(text):
            raw = m.group(0)
            ok = isbn13_valid(raw)
            isbns.append({"value": raw, "checksum_valid": ok})
    result["identifiers"] = {"doi": sorted(set(dois)), "isbn13": isbns}

    result["headers"] = headers
    result["footers"] = footers
    return result


# ---------------------------------------------------------------- 报告渲染

def render_text(r):
    out = []
    out.append("=" * 70)
    out.append("数学建模竞赛论文机械扫描报告")
    out.append("=" * 70)
    out.append("文件: %s" % r.get("file"))
    out.append("解析引擎: %s" % r.get("engine"))
    if r.get("error"):
        out.append("错误: %s" % r["error"])
        return "\n".join(out)
    out.append("页数来源: %s" % r.get("page_source", ""))
    out.append("总页数: %d%s" % (r["page_count"], "" if r.get("page_count_reliable") else "（不可靠，页数类判据须在导出 PDF 后复核）"))
    out.append("语言判定: %s (中文字符 %d, 拉丁字符 %d)" % (
        r["language"]["verdict"], r["language"]["cjk_chars"], r["language"]["latin_chars"]))
    if r.get("docx_headers_footers"):
        out.append("")
        out.append("[Word 页眉页脚]")
        for item in r["docx_headers_footers"]:
            out.append("  第 %d 节 页眉: %s" % (item["section"], item.get("header") or "空"))
            out.append("  第 %d 节 页脚: %s" % (item["section"], item.get("footer") or "空"))
        out.append("  提示：国赛规范明确要求论文不得有页眉，此处页眉非空即为违规")

    out.append("")
    out.append("[赛事信号]")
    s = r["signals"]
    out.append("  承诺书特征页: %s" % (s["cumcm_promise_pages"] or "无"))
    out.append("  编号专用页特征页: %s" % (s["cumcm_number_pages"] or "无"))
    out.append("  Summary Sheet 页: %s" % (s["mcm_summary_sheet_pages"] or "无"))
    out.append("  Report on Use of AI 页: %s" % (s["ai_use_report_pages"] or "无"))
    out.append("  目录页: %s" % (s["toc_pages"] or "无"))
    out.append("  含摘要字样页: %s" % (s["abstract_pages"] or "无"))

    out.append("")
    out.append("[页数合规]")
    predicted = " ".join(r.get("contest_prediction", {}).get("verdict", []))
    for pr in r.get("page_rules", []):
        applies_mcm = pr["rule"].startswith("MCM")
        if "MCM/ICM" in predicted and not applies_mcm:
            continue
        if "CUMCM" in predicted and applies_mcm:
            continue
        flag = {True: "通过", False: "不通过", None: "待人工判定"}[pr["passed"]]
        out.append("  [%s] %s | 实际 %s 页 | %s" % (flag, pr["rule"], pr["actual"], pr["note"]))

    out.append("")
    out.append("[美赛页眉检查]")
    h = r["mcm_header"]
    out.append("  匹配到 Team # 页眉的页数: %d / %d" % (h["found"], r["page_count"]))
    out.append("  控制号: %s" % (h["control_numbers"] or "无"))
    out.append("  页眉声明总页数: %s" % (h["declared_total"] or "无"))
    out.append("  缺失页眉的页: %s" % (h["missing_pages"] if h["missing_pages"] else "无"))
    if h["mismatch_pages"]:
        reasons = defaultdict(list)
        for item in h["mismatch_pages"]:
            reasons[item["reason"]].append(item["page"])
        for reason, pgs in reasons.items():
            out.append("  %s：共 %d 页，例 %s" % (reason, len(pgs), pgs[:10]))
    else:
        out.append("  页码与总页数声明均一致")

    out.append("")
    out.append("[赛事初判]")
    cp = r.get("contest_prediction", {})
    out.append("  判定: %s" % " / ".join(cp.get("verdict", [])))
    for b in cp.get("basis", []):
        out.append("  依据: %s" % b)
    if r.get("front_matter_pages"):
        out.append("  前置页（承诺书/编号专用页，身份信息按规范允许）: %s" % r["front_matter_pages"])
    if not r.get("front_matter_excluded", True):
        out.append("  注意：全文未切出独立前置页，身份扫描未排除承诺书内容，需人工区分")

    out.append("")
    out.append("[页眉检测]")
    if not r.get("suspected_header"):
        out.append("  未检出跨页重复的页眉行")
    for item in r["suspected_header"]:
        out.append("  重复出现 %d 次: %s" % (item["pages"], item["line"][:100]))

    out.append("")
    out.append("[身份泄露扫描]")
    if not r["identity_leaks"]:
        out.append("  未发现明显身份泄露特征")
    for item in r["identity_leaks"]:
        out.append("  * %s (命中 %d 处)" % (item["type"], item["count"]))
        for s2 in item["samples"]:
            out.append("      p.%d ... %s ..." % (s2["page"], s2["snippet"]))

    out.append("")
    out.append("[图表编号与正文引用一致性]")
    for item in r["figure_table_numbering"]:
        out.append("  * %s 共检出标题 %d 处" % (item["kind"], item["caption_count"]))
        out.append("      标题编号: %s" % ", ".join(item["caption_labels"][:60]))
        if item["duplicate_captions"]:
            out.append("      [问题] 重复定义的编号: %s" % item["duplicate_captions"])
        if item["missing_in_sequence"]:
            out.append("      [问题] 编号序列缺失: %s" % item["missing_in_sequence"])
        if item["cited_but_no_caption"]:
            out.append("      [问题] 正文引用了但不存在的编号: %s" % item["cited_but_no_caption"])
        if item["caption_never_cited"]:
            out.append("      [问题] 已定义但正文从未引用: %s" % item["caption_never_cited"])
        if not any([item["duplicate_captions"], item["missing_in_sequence"],
                    item["cited_but_no_caption"], item["caption_never_cited"]]):
            out.append("      编号连续、无重复、引用一一对应")

    out.append("")
    out.append("[公式编号]")
    out.append("  行末括号编号数: %d" % r["equation_numbering"]["count"])
    out.append("  前若干项: %s" % r["equation_numbering"]["items"][:20])

    out.append("")
    out.append("[引用与文献表]")
    rf = r["references"]
    out.append("  参考文献章节起始页: %s" % rf["section_page"])
    out.append("  文献条目数: %d" % rf["entry_count"])
    out.append("  文献编号: %s" % rf["entry_numbers"])
    out.append("  正文引用编号: %s" % rf["cited_numbers"])
    out.append("  正文引用但文献表未列: %s" % (rf["cited_not_listed"] or "无"))
    out.append("  文献表列出但正文未引: %s" % (rf["listed_not_cited"] or "无"))

    out.append("")
    out.append("[标识符]")
    out.append("  DOI (%d): %s" % (len(r["identifiers"]["doi"]), r["identifiers"]["doi"][:20]))
    out.append("  ISBN-13: %s" % (r["identifiers"]["isbn13"] or "无"))

    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="数学建模竞赛论文机械扫描")
    ap.add_argument("pdf", help="PDF 文件路径")
    ap.add_argument("--json", dest="json_out", help="输出 JSON 结果路径")
    ap.add_argument("--text", dest="text_out", help="输出文本报告路径")
    ap.add_argument("--password", default="", help="PDF 打开口令")
    args = ap.parse_args()

    result = scan(args.pdf, args.password)
    report = render_text(result)

    if args.text_out:
        with open(args.text_out, "w", encoding="utf-8") as f:
            f.write(report)
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    print(report)


if __name__ == "__main__":
    main()
