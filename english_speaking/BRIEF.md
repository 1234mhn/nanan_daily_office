# 任务：闯关式雅思英语口语练习页面（个人自用）

## 交付物
单文件 HTML（不需要服务器、不依赖联网 CDN，双击浏览器打开即可用；手机浏览器也能用）
文件：/root/.openclaw/workspace/english_speaking/ielts_speaking_quest.html

## 用户是谁
韩语/英语老师，自己练英语口语。要求：审美高、务实省力。

## 核心结构
1. 首页 = 关卡地图（grid 卡片）
   - 主题（Topic）分区，每个主题下若干关（Level）
   - 未解锁=灰锁 🔒，已过关=✅，当前关=高亮
   - 只有前一关"通过自评"才解锁下一关（同一主题内顺序解锁；主题之间也需要按顺序，第 1 个主题第 1 关默认可用）
   - 顶部总进度条：已过关数 / 总关数
2. 关口页（点进一关）
   - 题型标记：Part 1 / Part 2 / Part 3
   - 英文题目（大字）+ 中文小字翻译提示
   - 💡 提示词/思路 (Ideas & Keywords) 折叠区
   - 计时器：准备 30s/1min（Part2 给 1 分钟准备）+ 回答计时（Part1 30s，Part2 2min，Part3 1min），倒计时最后 10 秒变红
   - 🎤 录音按钮：MediaRecorder 录音，录完出现 audio 回放控件，可重录
   - 📖 示范答案折叠区（Sample Answer，英文 + 中文对照）
   - ✅ 自评过关按钮（"我练熟了 → 过关"），点击后：
     - 标记该关通过，解锁下一关
     - 存 localStorage
   - ← 返回地图

## 内容（第一版，自己写，要地道、难度梯度合理）
6 个主题 × 每主题 4 关 = 24 关：
1. Daily Life & Hometown（日常与家乡）— Part1
2. Food & Restaurant（饮食）— Part1
3. Travel & Transport（旅行）— Part2
4. Work & Study（工作学习）— Part1
5. Technology & Internet（科技网络）— Part3
6. Opinions & Society（观点与社会）— Part3

每关内容：
- question_en / question_zh
- type（Part1/2/3）
- ideas: 3-5 条英文思路关键词（带中文小注）
- sample_en（示范答案，Part1 约 50-70 词，Part2 约 150-180 词并含 1 分钟结构，Part3 约 80-100 词）
- sample_zh（中文翻译）

## 技术要求
- 纯原生 HTML/CSS/JS，无框架，无外部请求（不引 CDN 字体/库）
- 数据用 JS 数组常量写在文件里，与渲染逻辑分离，方便以后加题
- 设计：干净现代、深色或浅色皆可（选一套统一配色），卡片圆角、留白舒服、响应式（手机单列）
- localStorage key: ielts_speaking_quest_v1
- 代码注释清晰，文件顶部写「如何加新题」的说明
- 中文界面为主，英文题目/答案保留英文

## 约束
- 一次性写出完整可运行文件，不要 TODO 占位
- 不要删改工作区其它文件
