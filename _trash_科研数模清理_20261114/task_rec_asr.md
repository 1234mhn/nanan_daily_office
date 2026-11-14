# 任务：给韩语单词岛屿「造句练习」加录音按钮（腾讯云语音识别）

## 背景
用户手机上浏览器语音识别（Web Speech API）用不了（微信内+国内浏览器都不支持）。
已确认改用**腾讯云「一句话识别」**，服务已开通，凭据在服务器上（`~/.tccli/default.credential`，secretId/secretKey），**已验证可调通**。

## 目标
在「造句练习」段落加一个 🎤 按钮：
**点按钮 → 录一段语音 → 上传服务器 → 腾讯云识别韩语 → 文字自动填进输入框**
→ 用户再点「✅ 检查句子」→ DeepSeek 纠错

## 文件位置
- 前端：`/www/korean_vocab/index.html`（真实路径是 **下划线** `/www/korean_vocab/`）
- 后端：`/www/korean_vocab/server/app.js`（已有 `/api/correct` 纠错接口）
- 服务：systemd `korean-vocab-api.service`（端口 3210）

**改前备份**：
- `cp /www/korean_vocab/index.html /www/korean_vocab/index_backup_$(date +%Y%m%d_%H%M)_before_rec.html`
- `cp /www/korean_vocab/server/app.js /www/korean_vocab/server/app.js.bak_$(date +%Y%m%d_%H%M)`

## 后端：新增 POST /api/asr
接收前端上传的音频（base64 或 raw body），调用腾讯云「一句话识别」：

- 接口：`SentenceRecognition`
- 参数：
  - `EngSerViceType`: `16k_ko`（16k 韩语）
  - `SourceType`: `1`（音频数据直传）
  - `VoiceFormat`: 按上传格式（wav / webm 转换后 / mp3）
  - `Data`: base64 音频
  - `DataLen`: 音频字节数
- 鉴权：用 `~/.tccli/default.credential` 里的 secretId/secretKey，做 **TC3-HMAC-SHA256 签名**（区域 ap-shanghai，service asr，版本 2019-06-14）
  - 不要引入庞大的 tencentcloud-sdk-nodejs（可手写签名，约 60 行）；若装 SDK 更稳就用 SDK（`npm i tencentcloud-sdk-nodejs-asr`）
  - **密钥不要硬编码**，从 `/root/.tccli/default.credential` 读取（运行时读，不写进代码）
- 返回：`{ "text": "识别出的韩文" }`
- 错误处理：超时 30s、失败返回友好错误

### 音频格式处理（重要）
浏览器 `MediaRecorder` 一般录出来是 **webm/opus**，而腾讯云一句话识别支持的格式有限（wav/pcm/mp3/m4a 等）。
方案任选其一：
1. 前端用 `MediaRecorder` 录 **audio/webm**，服务器用 `ffmpeg` 转成 **wav 16k 单声道** 再上传（推荐，服务器已装还是先检查 `which ffmpeg`，没装就 `apt install -y ffmpeg`）
2. 或前端直接录 wav（AudioWorklet 手写较复杂，不推荐）

→ **推荐方案 1**：前端上传 webm，服务器 ffmpeg 转 wav → base64 → 调腾讯云。

## 前端：恢复 🎤 按钮（录音版）
当前「造句练习」段落（约 3375 行附近）现在只有一个提示条 + 检查按钮。

改为：
```html
<div class="input-controls">
  <button class="voice-btn" id="voiceBtn">🎤 按住说话</button>
  <button class="check-btn" id="checkBtn">✅ 检查句子</button>
</div>
```
交互（两种都做，移动端优先"按住"）：
- **按住说话（touchstart 开始录 / touchend 停止并上传）**，同时兼容点击切换（PC 用）
- 录音中按钮显示「🔴 识别中…」并加 class `recording`（脉冲动画）
- 上传中显示「⏳ 识别中…」
- 成功：识别文字**追加/填入** textarea，并 focus
- 失败：alert 友好提示（如"网络或识别失败，请重试，或直接打字"）

用 `navigator.mediaDevices.getUserMedia({audio:true})` + `MediaRecorder`。
⚠️ getUserMedia 在**非 HTTPS 下不可用**，本站是 HTTPS ✅；微信内置浏览器也支持 getUserMedia 录音 ✅

## 样式
- `.voice-btn`：浅色底、圆角，`flex: 0 0 auto`
- `.voice-btn.recording`：红色系 + 脉冲动画
- 保留原有 `.voice-tip` 提示条，但文案改为：「按住 🎤 说韩语，自动转成文字；也可以直接打字」

## 自检（务必做）
1. 主界面（homePage）区块与 `/www/korean_vocab/index_backup_20260920_2003_before_themepage_redesign.html` **逐字节对比一致**
2. `curl -X POST http://127.0.0.1:3210/api/asr --data-binary @test.wav -H 'Content-Type: audio/wav'` 能返回识别文字（可用 ffmpeg 生成一段测试音频，或先静音 wav 验证链路通）
3. `curl -X POST https://nannan2026.cn/api/asr` 线上可通（nginx `/api/` 已代理到 3210）
4. `systemctl is-active korean-vocab-api` = active
5. 页面 200

## 输出
- 改了什么（分条）
- 测试结果（asr 接口实测返回）
- 确认主界面未动
- 使用说明（手机怎么用）
