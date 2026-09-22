# Windows / 编译环境实测坑与绕行方案

本文件记录真实竞赛论文全流程中实际踩到并验证过解法的问题。遇到下述症状时按方案处理，不要现场重试猜测。

## 1. PDF 题面/文献文本提取乱码

**症状**：`pdftotext` 输出是 CJK 方块或乱码（部分 PDF 文本层是 UTF-16 内码，旧版 pdftotext 4.00 会误读）。
**方案**：放弃文本层，`pdftoppm -png -r 150 某.pdf page` 渲染逐页 PNG 后用视觉能力读图。2~3 页的题面此法最可靠。
**注意**：本环境 `/tmp` 不可靠，输出一律写到明确的 Windows 路径；管道里传中文用 `PYTHONIOENCODING=utf-8 python -c` 而非 grep。

## 2. xelatex 报 "MiKTeX cannot retrieve attributes for the directory '...python.exe\'"

**根因**：系统 PATH 中存在**文件**条目（如把 `...\Python312\python.exe` 写成 PATH 项），MiKTeX 启动时把 PATH 条目全当目录扫描，撞上文件直接崩溃。
**绕行**（不改系统）：编译子进程用清理过的 PATH 前缀，例如 Git Bash：

```bash
CLEANPATH="/c/Users/段静/AppData/Local/Programs/MiKTeX/miktex/bin/x64:/c/Windows/system32:/c/Windows:/c/Windows/System32/Wbem:/c/Windows/System32/WindowsPowerShell/v1.0:/c/Windows/System32/OpenSSH:/usr/bin"
PATH="$CLEANPATH" xelatex -interaction=nonstopmode main.tex
```

**根治**（经用户授权）：用 PowerShell 备份 `[Environment]::GetEnvironmentVariable('Path','Machine')` 到文件，删除文件型条目/孤立 `%`/`%VAR%` 残片/空条目后写回（machine 级需 UAC 提权）。修复后用注册表重建的环境验证：`$env:Path=[Environment]::GetEnvironmentVariable('Path','Machine')+';'+[Environment]::GetEnvironmentVariable('Path','User')` 再跑 xelatex。已在运行的程序要重启才读到新 PATH。

## 3. MiKTeX 缺宏包（如 kvsetkeys.sty not found）

**方案**：优先**移除非必需宏包**（如 hyperref 仅加链接功能时可直接删），不要现场装包（MiKTeX 自动安装可能被禁用并伴随 "not checked for updates" 干扰信息）。

## 4. fancyvrb 附录代码清单

- `breaklines` 是 **listings** 的键，`\VerbatimInput` 不认（报 keyval Error）；fancyvrb 不折行，用 `fontsize=\tiny` + `frame=single` 控制宽度即可。
- 代码注释含希腊字母（μ δ σ θ…）时 lmmono 字体无字形，编译静默丢字。**修法**（代码保持逐字节不变）：

```latex
\xeCJKDeclareCharClass{CJK}{"03B1, "03B4, "03B8, "03BC, "03C3}
```

## 5. "Missing character" 静默丢字

全角标点（，；：（））落在数学模式里会被西文字体静默丢弃。**验收必查**：`grep -c "Missing character" 编译日志`，非零即返工——把标点移进 `\text{}`。

## 6. 摘要框花括号配对

`\fbox{\parbox{...}{...}}` 手写层数极易错（多一层就是 "Too many }'s"）。**用环境替代手配**：

```latex
\noindent\fbox{\begin{minipage}{\dimexpr\textwidth-2\fboxsep-2\fboxrule\relax}
...摘要正文...
\end{minipage}}
```

## 7. 生成 LaTeX/脚本时的转义陷阱

用 Bash heredoc 内联 Python 写含反斜杠的内容时，`\U`（如 `C:\Users`）、`\x` 会被当转义（`C:\Users` → `ìJK...`），且有时**静默成功**。**纪律**：改写文件一律用文件编辑工具写 Python 脚本再执行；反斜杠用 `chr(92)` 构造；动手前先 `cat -A` 看文件现场，改完 grep 验证关键字节。

## 8. 编译退出码非零但 PDF 已生成

xelatex 在 nonstopmode 下出错仍可能产出 PDF。**以日志为准**：`grep -c "^!" 日志` 为 0 才算编译通过；同时检查 Overfull（>10pt 的文本越界）与 Missing character。
