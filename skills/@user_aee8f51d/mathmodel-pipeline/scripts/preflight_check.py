#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mathmodel-pipeline 依赖预检脚本（仅标准库，无第三方依赖）。

按任务类型判断缺失依赖是否阻塞：
    analysis  赛题分析：只需 Python 本体
    code      编码求解：numpy / pandas / matplotlib 阻塞，其余建议
    paper     论文编译：typst 或 xelatex 至少其一
    word      Word 交付：pandoc 或 pypandoc 至少其一
    all       以上全部（默认）

用法：
    python preflight_check.py --profile code
    python preflight_check.py --profile all --json
    python preflight_check.py --profile all --strict   # 阻塞项缺失时退出码 1
"""
import argparse
import importlib.util
import json
import os
import shutil
import sys

CORE_PACKAGES = ["numpy", "pandas", "matplotlib", "openpyxl"]
EXTENDED_PACKAGES = ["scipy", "statsmodels", "seaborn", "pingouin", "pint", "uncertainties", "requests"]
PAPER_COMMANDS = ["typst", "xelatex"]
WORD_PACKAGES = ["pypandoc"]
WORD_COMMANDS = ["pandoc"]
RENDER_COMMANDS = ["pdftoppm", "mutool", "magick"]  # 任一即可，用于 PDF 视觉检查
OPTIONAL_COMMANDS = ["drawio"]


def check_packages(names):
    found, missing = [], []
    for name in names:
        (found if importlib.util.find_spec(name) is not None else missing).append(name)
    return found, missing


def check_commands(names):
    found, missing = [], []
    for name in names:
        (found if shutil.which(name) else missing).append(name)
    return found, missing


def run(profile):
    py_ok = sys.version_info >= (3, 10)
    core_found, core_missing = check_packages(CORE_PACKAGES)
    ext_found, ext_missing = check_packages(EXTENDED_PACKAGES)
    word_found, word_missing = check_packages(WORD_PACKAGES)
    paper_found, paper_missing = check_commands(PAPER_COMMANDS)
    word_cmd_found, word_cmd_missing = check_commands(WORD_COMMANDS)
    render_found, _ = check_commands(RENDER_COMMANDS)
    _, optional_missing = check_commands(OPTIONAL_COMMANDS)

    openalex = "configured" if os.environ.get("OPENALEX_API_KEY") else "not configured"

    blockers, advisories = [], []

    if not py_ok:
        blockers.append("Python >= 3.10（当前 %d.%d.%d）" % sys.version_info[:3])

    if profile in ("code", "all"):
        blockers += [f"Python 包 {name}" for name in core_missing]
        advisories += [f"建议安装 Python 包 {name}" for name in ext_missing]
    elif profile == "analysis":
        advisories += [f"建议安装 Python 包 {name}" for name in core_missing + ext_missing]

    if profile in ("paper", "all") and not paper_found:
        blockers.append("typst 与 xelatex 均缺失（论文编译至少需要其一）")
    if profile in ("word", "all") and not word_found and not word_cmd_found:
        blockers.append("pandoc 与 pypandoc 均缺失（Word 导出至少需要其一）")
    if profile in ("word", "all") and word_cmd_found and not word_found:
        advisories.append("pandoc 可用；安装 pypandoc-binary 可让导出脚本自动定位")

    if profile in ("paper", "all") and not render_found:
        advisories.append("pdftoppm / mutool / magick 均缺失：PDF 视觉检查将只能做程序化检查")
    for name in optional_missing:
        advisories.append(f"可选工具 {name} 缺失：不影响流程，仅 .drawio 无法导出 PDF")

    result = {
        "profile": profile,
        "python": {"version": ".".join(map(str, sys.version_info[:3])), "ok": py_ok},
        "packages": {
            "core_found": core_found, "core_missing": core_missing,
            "extended_found": ext_found, "extended_missing": ext_missing,
            "word_found": word_found, "word_missing": word_missing,
        },
        "commands": {
            "paper_found": paper_found, "paper_missing": paper_missing,
            "word_found": word_cmd_found, "word_missing": word_cmd_missing,
            "render_found": render_found,
        },
        "env": {"OPENALEX_API_KEY": openalex},
        "blockers": blockers,
        "advisories": advisories,
        "ok": len(blockers) == 0,
    }
    return result


def render_text(r):
    lines = []
    lines.append(f"依赖预检（profile={r['profile']}）: "
                 + ("通过" if r["ok"] else "存在阻塞项"))
    lines.append(f"  Python {r['python']['version']}: " + ("OK" if r["python"]["ok"] else "版本过低"))
    p = r["packages"]
    lines.append(f"  核心包 已装 {len(p['core_found'])} 缺 {len(p['core_missing'])}"
                 + (f"（缺: {', '.join(p['core_missing'])}）" if p["core_missing"] else ""))
    lines.append(f"  扩展包 已装 {len(p['extended_found'])} 缺 {len(p['extended_missing'])}"
                 + (f"（缺: {', '.join(p['extended_missing'])}）" if p["extended_missing"] else ""))
    c = r["commands"]
    lines.append(f"  论文编译器: {', '.join(c['paper_found']) or '无'}")
    lines.append(f"  Word 导出: {', '.join(c['word_found'] + p['word_found']) or '无'}")
    lines.append(f"  PDF 渲染: {', '.join(c['render_found']) or '无'}")
    lines.append(f"  OPENALEX_API_KEY: {r['env']['OPENALEX_API_KEY']}")
    if r["blockers"]:
        lines.append("  阻塞项:")
        lines += [f"    - {b}" for b in r["blockers"]]
    if r["advisories"]:
        lines.append("  建议:")
        lines += [f"    - {a}" for a in r["advisories"]]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="mathmodel-pipeline 依赖预检")
    parser.add_argument("--profile", choices=["analysis", "code", "paper", "word", "all"], default="all")
    parser.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    parser.add_argument("--strict", action="store_true", help="阻塞项缺失时以退出码 1 结束")
    args = parser.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    result = run(args.profile)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_text(result))
    if args.strict and not result["ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
