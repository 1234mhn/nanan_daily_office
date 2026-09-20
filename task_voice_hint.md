# 任务：优化韩语单词岛屿「造句练习」的语音输入引导

## 背景
用户手机（国内安卓，可能无 Google 服务）上，网页语音识别（`webkitSpeechRecognition`）**用不了**——微信里不行，手机浏览器里也不行。

原因：国内安卓浏览器 + 无 Google 框架 → Web Speech API 失效。

## 解决方案
改用**手机键盘自带的语音输入**（讯飞/百度引擎，识别韩语更准，不受浏览器限制）。

## 目标文件
`/www/korean_vocab/index.html`

⚠️ 真实路径 `/www/korean_vocab/`（**下划线**目录）。
**改前备份**：`cp index.html index_backup_$(date +%Y%m%d_%H%M)_before_voice_hint.html`

## 范围限制
- ✅ 只改「段落6：造句练习」那段（`sentence-practice` 相关 HTML/CSS/JS）
- ❌ 主界面（homePage）绝对不要动
- ❌ 其他段落不要动
- ❌ 主题数据不要动

## 具体改动

### 1. 删掉没用的 🎤 语音输入按钮
当前代码（约 3381-3388 行）：
```html
<div class="input-controls">
  <button class="voice-btn" id="voiceBtn" title="点击开始语音识别">
    🎤 语音输入
  </button>
  <button class="check-btn" id="checkBtn">
    ✅ 检查句子
  </button>
</div>
```

改为：**移除 voice-btn**，只留检查按钮，并在输入框上方/下方加一个清晰的引导提示条：

```html
<div class="voice-tip">
  💡 点输入框，用手机键盘上的 🎤 麦克风说韩语（记得键盘要切到韩语输入）
</div>
<div class="input-controls">
  <button class="check-btn" id="checkBtn">✅ 检查句子</button>
</div>
```

### 2. 清理对应的 JS
- 删除 `initSentencePractice` 里所有 `SpeechRecognition` / `recognition` 相关代码（约 4435-4500 行）
- 只保留 `checkBtn` 的点击逻辑（调 `/api/correct`）

### 3. 提示条样式
新增 `.voice-tip` 样式：
- 浅色背景（如 `#F5F9F7`）、圆角、小字、左边框或图标
- 配色跟页面协调（用现有变量如 `--sage`、`--line`、`--ink-3`）
- 移动端字号 .85rem 左右，padding 10-12px

### 4. 输入框 placeholder 优化
改为：`点这里，用键盘麦克风说韩语，或直接打字…`

## 自检（务必做）
1. 主界面（homePage）区块与备份**逐字节对比一致**
2. 页面能正常打开（curl -sI https://nannan2026.cn/korean-vocab/ 返回 200）
3. 检查按钮功能正常（POST /api/correct 仍可调通）
4. 全文不应再有 `SpeechRecognition`、`voiceBtn`、`recognition` 残留引用

## 输出
- 改了什么（分条）
- 确认主界面未动
- 确认无残留 SpeechRecognition 引用
