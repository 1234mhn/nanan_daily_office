# -*- coding: utf-8 -*-
"""mathmodel-pipeline 技能自带回归测试。

用法：python tests/self_test.py
覆盖：frontmatter 规范、引用完整性、门禁模板、EVIDENCE_GAP 双向协议、
      无人值守降级、目录口径、附录口径唯一、动态问题数、文风卫生、
      资产模板质量。全部断言通过以退出码 0 结束。
"""
import io
import re
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok))
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail and not ok else ""))


def read(p):
    return io.open(p, encoding="utf-8").read()


skill_text = read(SKILL_DIR / "SKILL.md")
contracts = read(SKILL_DIR / "references/stage-contracts.md")
grill = read(SKILL_DIR / "references/grill-protocol.md")
checklist = read(SKILL_DIR / "references/verification-checklist.md")
pitfalls = read(SKILL_DIR / "references/windows-pitfalls.md")
template = read(SKILL_DIR / "assets/templates/cumcm/main.tex")
readme = read(SKILL_DIR / "README.md")
all_text = skill_text + contracts + grill + checklist

# ---- 1. frontmatter 与结构 ----
m = re.match(r"^---\s*\n(.*?)\n---\s*\n", skill_text, re.S)
check("SKILL.md 有 frontmatter", bool(m))
fm = m.group(1) if m else ""
name_m = re.search(r"^name:\s*(.+)$", fm, re.M)
check("name 为 kebab-case 且与目录名一致",
      bool(name_m) and name_m.group(1).strip() == SKILL_DIR.name)
desc_m = re.search(r"^description:\s*(.+)$", fm, re.M)
desc = desc_m.group(1) if desc_m else ""
check("description 含核心触发词", all(w in desc for w in ["数学建模", "国赛", "论文"]))
check("description 覆盖口语化触发", "数模题" in desc)
check("SKILL.md 正文 < 500 行（渐进式披露）",
      skill_text.count("\n") + 1 < 500, f"{skill_text.count(chr(10)) + 1} 行")

# ---- 2. 引用完整性 ----
for ref in ["references/stage-contracts.md", "references/grill-protocol.md",
            "references/verification-checklist.md", "references/windows-pitfalls.md",
            "assets/templates/cumcm/main.tex", "scripts/preflight_check.py"]:
    check(f"SKILL.md 引用的 {ref} 存在", (SKILL_DIR / ref).exists())
check("README.md 存在", (SKILL_DIR / "README.md").exists())

refs = set(re.findall(r"\$([a-z][a-z0-9-]{3,})", all_text))
check("无悬空的 $skill 引用", refs <= {SKILL_DIR.name}, str(refs))
check("无 superpowers: 旧命名空间残留", "superpowers:" not in all_text)
check("不引用不存在的 statistical-power skill", "statistical-power" not in all_text)

# ---- 3. 门禁进流程模板 ----
check("plan.md 模板包含门禁A", "[门禁A]" in skill_text)
check("plan.md 模板包含门禁B", "[门禁B]" in skill_text)
check("plan.md 模板包含门禁C", "[门禁C]" in skill_text)
check("todo.md 模板同样包含三门禁", skill_text.count("- [ ]") >= 9)

# ---- 4. EVIDENCE_GAP 双向协议 ----
check("产生方（分析报告模板）有 EVIDENCE_GAP 登记", contracts.count("EVIDENCE_GAP 登记") >= 2)
check("SKILL.md 定义双向职责（产生方标记+消费方核销）",
      "产生方" in skill_text and "消费方" in skill_text)
check("门禁协议定义 EVIDENCE_GAP 三选一处理", "删除无证据论点" in grill and "降低结论强度" in grill)

# ---- 5. 验收返工规则 ----
check("SKILL.md 有返工分类表", "FAIL 类别" in skill_text and "退回步骤" in skill_text)
check("有同题重复失败熔断（2 轮后停止猜测）", "超过 2 轮" in skill_text)

# ---- 6. 无人值守降级 ----
check("SKILL.md 定义无人值守降级", "无人值守降级" in skill_text and "READY_WITH_RISKS" in skill_text)
check("降级时标注[默认采用（未经用户确认）]", "默认采用（未经用户确认）" in grill)
check("默认决定汇总进 VERIFY_REPORT", "默认采用决策清单" in checklist)

# ---- 7. 统一目录口径 ----
check("明确 results/ 为唯一结果目录",
      "唯一的真实运行产物目录" in skill_text or "唯一结果目录" in skill_text)
check("显式禁止另造 code/outputs", "不要另造" in skill_text and "code/outputs" in skill_text)

# ---- 8. 附录口径唯一 ----
appendix_fail = len(re.findall(r"^.*附录未包含本次运行所用完整源代码.*FAIL", checklist, re.M))
check("附录缺源代码在清单中仅一处判定且为 FAIL", appendix_fail == 1, f"{appendix_fail} 处")
check("无附录 WARN 旧口径", "附录只有命令" not in checklist)

# ---- 9. 动态问题数 ----
check("无硬编码三问报告结构", "问题三结果" not in all_text and "问题三" not in all_text)
check("无固定 problem3 文件", "problem3" not in all_text)
check("使用 Q1..Qn 动态记法", "Q1..Qn" in all_text)

# ---- 10. 实测经验固化 ----
check("SKILL.md 落实判据预登记纪律", "必须在查看数据计算之前写入建模报告" in skill_text)
check("阶段契约含拟合防错清单", "参数可辨识性" in contracts and "粗差识别即弃用" in contracts)
check("环境坑参考覆盖 MiKTeX PATH 崩溃", "cannot retrieve attributes" in pitfalls)
check("环境坑参考覆盖 Missing character 检查", "Missing character" in pitfalls)

# ---- 11. CUMCM 模板资产质量 ----
check("模板含希腊字母 CJK 映射（防附录丢字）", "xeCJKDeclareCharClass" in template)
check("模板摘要框用 minipage 而非 parbox（防花括号错配）",
      "fbox{\\begin{minipage}" in template and "\\parbox" not in template)
check("模板无 fancyvrb 不支持的 breaklines 键", "breaklines" not in template)
check("模板为占位符骨架（⟨⟩ 标记待填内容）", "⟨" in template)

# ---- 12. README ----
check("README 含安装/使用/测试/致谢章节",
      all(s in readme for s in ["## 安装", "## 使用", "## 测试与验证", "## 致谢"]))
check("README 记录实测验证（CUMCM 2025 B）", "CUMCM 2025" in readme or "2025 高教社杯" in readme)

# ---- 13. 预检脚本可执行 ----
r = subprocess.run([sys.executable, str(SKILL_DIR / "scripts/preflight_check.py"), "--help"],
                   capture_output=True, text=True)
check("preflight_check.py --help 正常退出", r.returncode == 0)

failed = [n for n, ok in RESULTS if not ok]
print()
print(f"共 {len(RESULTS)} 项断言，通过 {len(RESULTS) - len(failed)}，失败 {len(failed)}")
sys.exit(1 if failed else 0)
