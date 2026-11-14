# 任务：改写韩语单词岛屿「主题内页」（闯关地图页）的样式

## 用户明确意图（关键）
用户说：**「每一个主题下面点开之后，各主题它的页面就是这种的」**
→ 也就是：点击主页某个主题后进入的**主题内页**，要改成用户发来的参考截图那种样式。

参考截图路径（你自己读图）：
- `/root/.openclaw/workspace/media/tmp_review/ref_style.jpg`（用户给的目标样式）
- 也可参考 `/root/.openclaw/workspace/media/tmp_review/shot_top.jpg` / `shot_mid.jpg` / `shot_bot.jpg`

## 目标文件（路径已确认，不要再到处找）
`/www/korean_vocab/index.html`（约 165KB）

⚠️ 注意：文件在 `/www/korean_vocab/`（**下划线**目录）。不要找 `/www/korean-vocab/`（不存在）。

## 当前相关代码位置
- 主题内页 = `questMapPage` 区块（HTML 里 `<div id="questMapPage" class="hidden">`）
- 相关样式：`.quest-map`、`.map-header`、`#questGroups`
- 渲染逻辑：找 `questGroups` 相关的 JS 函数

## 第一步：先读图 + 对照代码（本轮不改）
1. 读参考截图，如实描述主题内页长什么样（布局/元素/配色/交互）
2. 读 `/www/korean_vocab/index.html` 中 `questMapPage` 区块的 HTML + CSS + JS
3. 列出「截图 vs 当前主题内页」的**具体差异清单**
4. 给出改动方案（逐条列位置 + 改什么）

## 第二步：汇报后停下等我确认
**本轮只做分析，绝不修改文件。** 输出报告后停下。

## 报告格式
- 截图描述（要点）
- 当前主题内页结构（HTML/CSS/JS 位置）
- 差异清单（表格）
- 改动方案（分条，注明改动位置）
