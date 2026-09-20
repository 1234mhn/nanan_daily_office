# 任务：给韩语单词岛屿「造句练习」加语音输入 + AI 纠错

## 用户需求
在韩语单词岛屿的**造句练习**段落，加上：
1. 🎤 语音输入按钮 → 浏览器语音识别（韩语 ko-KR）→ 识别结果填入输入框
2. 识别后自动调 AI（DeepSeek）**纠错**：给出修改后的句子 + 错在哪 + 更地道说法

## 前端文件
`/www/korean_vocab/index.html`

⚠️ 真实路径是 `/www/korean_vocab/`（**下划线**目录）。不要找 `/www/korean-vocab/`（不存在）。

**改前必须备份**：`cp index.html index_backup_$(date +%Y%m%d_%H%M)_before_speech_correct.html`

## 范围限制（重要）
- ✅ 只改**学习页的「段落6：造句留白」**那段（当前代码：`<div class="blank-area">（留白，供手写/自测）</div>`，在 buildSteps 之类的函数里）
- ✅ 可以新增：语音输入按钮样式 + JS
- ❌ **主界面（homePage）绝对不要动**
- ❌ 不要动其他段落（①~⑤）
- ❌ 不要动主题数据

## 后端服务（新建）
在服务器上新建一个轻量 Node 服务，例如 `/www/korean_vocab/server/app.js`（或 `/opt/korean-vocab-api/`）：

- 提供 `POST /api/correct`，接收 `{ text: "学生说的韩语句子", word: "当前学习的韩语单词" }`
- 调用 DeepSeek API：
  - Base URL: `https://api.deepseek.com/v1`
  - **API key 从环境变量读**：`process.env.DEEPSEEK_API_KEY`（服务器已配置，不要硬编码！）
  - 模型：`deepseek-v4-flash`
  - System prompt 要求：韩语老师角色，纠正学生造句的语法/助词/语序/拼写错误，返回 JSON：
    ```json
    {
      "original": "学生的原句",
      "corrected": "修改后的句子",
      "isCorrect": true/false,
      "issues": ["错误1说明", "错误2说明"],
      "better": "更地道的说法（可选）"
    }
    ```
- 端口：例如 3210（不要占用已有端口，先 `ss -tlnp` 检查）
- 加 CORS 头（同域名其实不需要，但加上更稳）
- 加超时（如 20s）和错误处理

## nginx 配置
在 `/etc/nginx/sites-enabled/default` 的 **https server 块**里（含 `nannan2026.cn` 的那个）加：
```nginx
location /api/ {
    proxy_pass http://127.0.0.1:3210/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_read_timeout 30s;
}
```
⚠️ 改 nginx 前先备份：`cp /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default_backup_$(date +%Y%m%d_%H%M)_before_api`
⚠️ 只**新增** location，不要动其他配置
⚠️ 改完 `/usr/sbin/nginx -t` 测试，再 `/usr/sbin/nginx -s reload`

## 前端交互设计
在造句练习段落里：
1. 一个**输入框**（textarea，学生可手打也可语音填）
2. 一个 **🎤 语音输入按钮**：
   - 用 `webkitSpeechRecognition` / `SpeechRecognition`，`lang='ko-KR'`，`interimResults=true`
   - 点击开始识别，再点停止
   - 实时把识别结果填入 textarea
   - 不支持时（如老 iOS）按钮置灰并提示"请用手机键盘语音输入"
3. 一个 **✅ 检查按钮**：
   - 把 textarea 内容 + 当前单词 POST 到 `/api/correct`
   - 显示结果：修改后句子（绿色）、错误说明列表、更地道说法
   - 加载中要有 loading 提示
   - 请求失败要有友好提示

## 自检（务必做）
1. 主界面（homePage）区块与备份文件**逐字节对比一致**
2. curl 本地测后端：`curl -X POST http://127.0.0.1:3210/api/correct -H 'Content-Type: application/json' -d '{"text":"저는 학교에 가요","word":"가다"}'` 能返回 JSON
3. curl 测线上：`curl -X POST https://nannan2026.cn/api/correct ...` 能通
4. `/usr/sbin/nginx -t` 通过
5. 页面能正常打开

## 服务守护
用 systemd 建一个 service（如 `korean-vocab-api.service`）保证开机自启、崩溃重启：
- ExecStart: `node /www/korean_vocab/server/app.js`
- EnvironmentFile 或 Environment= 注入 DEEPSEEK_API_KEY（从 /root/.openclaw/openclaw.json 或环境变量取）
- 注意：不要把 key 提交到任何可能公开的地方

## 输出
- 改了什么（分条）
- 后端服务状态（`systemctl status korean-vocab-api`）
- 测试结果（3 条 curl）
- 确认主界面未动
