# 任务：韩语课程页「造句区」语音输入功能（方案甲）

## 目标文件
`/www/korean_course/index.html`（线上 https://nannan2026.cn/korean/）

## 🔴 铁律（必须遵守）
1. **改之前先备份**：`cp /www/korean_course/index.html /www/korean_course/index.html_backup_$(date +%Y%m%d_%H%M)_before_speechwrite.html`
2. **只加功能，不许动任何已有内容**（台词/单词/语法/例句/音变一个字都不能改）
3. **改完必须回归检查**：确认 20 个 pageLesson 页、238 个 📍单词、195 个 📌语法 数量不变
4. 做完报告：备份文件名 + 回归检查结果

## 用户需求（原话）
> "你造5个句子的话，那也点不开呀，那框里面最好是语音输入那种的哈。然后直接语音输入转韩文那种的。"

## 功能定义

在每个 `.line-exp` 讲解块的**末尾**，追加一个「✍️ 造句练习」区块：

### 结构
```
✍️ 造句练习（点麦克风，说韩语，自动转韩文）
┌──────────────────────────────┐
│ 1. [________________]  🎤 🔊  │
│ 2. [________________]  🎤 🔊  │
│ 3. [________________]  🎤 🔊  │
│ 4. [________________]  🎤 🔊  │
│ 5. [________________]  🎤 🔊  │
└──────────────────────────────┘
[💾 已自动保存]
```

### 每句包含
- 一个可编辑输入框（contenteditable 或 input，手机键盘友好）
- 🎤 语音输入按钮：点击开始录音，用 **Web Speech API**（`webkitSpeechRecognition`），`lang='ko-KR'`，识别结果**追加/填入**输入框
- 🔊 播放按钮：用页面已有 `speak()` 函数朗读该框内容
- 录音中按钮变红 + 脉冲动画，再点停止

### 数据保存
- 用 `localStorage` 保存，key 格式：`korean_sentence_{课号}_{句号}_{1~5}`
- 输入框内容变化即存（debounce 500ms）
- 页面加载时回填
- 显示"已自动保存"提示 1 秒后淡出

### 兼容与降级
- **必须检测浏览器支持**：`if (!(window.SpeechRecognition || window.webkitSpeechRecognition))` → 🎤 按钮置灰 + title 提示"浏览器不支持，请用 Chrome/Safari 打开"
- 不支持时**输入框和播放键照常可用**（保底）
- 微信内置浏览器大概率不支持 → 静默降级即可，不弹报错

### 样式
- 沿用页面现有风格（浅色 + 深色模式都要适配）
- 输入框：白底、1px 边框、圆角 8px、focus 时边框变蓝
- 深色模式：`body.dark` 下背景 #161b22、边框 #30363d
- 5 个输入框之间间距 8px
- 区块标题用 `<div class="sec">` 风格保持一致

## 技术要点
- **不要引任何外部库/CDN**（页面要求无外部依赖）
- 用纯原生 JS，自定义事件必须用 `event.stopPropagation()` 防止触发外层 `.line-hd` 的折叠
- 注入方式建议：写一个 `injectSentencePractice()` 函数，在 DOMContentLoaded 后遍历所有 `.line-exp` 追加
- 注意：`.line-exp` 是 `display:none` 的，注入要在隐藏状态下也能正常完成（不影响布局）
- 每页（pageLesson）的课号从 `page.id.match(/pageLesson(\d+)/)` 提取
- 句号从 `.kr` 文本开头的数字提取（如 "1. 운동을..."→ 1）

## 交付要求
- 代码注释清晰（中文）
- 改完自测：`node -e` 检查所有 `<script>` 块语法通过
- 报告：新增代码行数、备份文件名、回归检查结果
- **不要动 /www/korean_vocab/ 和 /www/korean_course/ 下其他文件**
