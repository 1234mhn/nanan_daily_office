# 任务：可爱风「主题词汇闯关」英语学习页面（个人自用）—— 改版

## 交付物
单文件 HTML（无外部依赖、无联网CDN、双击浏览器可开、手机可用）
文件：/root/.openclaw/workspace/英语/english_speaking/vocab_quest.html
（保留旧文件 ielts_speaking_quest.html 不要动）

## 用户
英语/韩语老师，自用练英语词汇。审美好，喜欢务实省力。要求界面「可爱一些」。

## 视觉风格（重点！可爱风）
- 马卡龙/糖果配色（奶油黄、薄荷绿、蜜桃粉、婴儿蓝、薰衣草紫），浅色背景 + 柔和阴影
- 大圆角（16-24px）、圆润字体感（用系统字体栈，font-weight 偏厚）
- emoji 当图标（🗺️ 🌱 🍰 ✈️ 💼 💻 🗣️ ⭐ 🎉 🔒 🔥）
- 关卡地图做成「小径/岛屿连线」感觉：每关一个圆形气泡按钮，之间用虚线连接；已过关=彩色+⭐，当前关=放大微微弹跳，未解锁=灰色🔒
- 动效：按钮hover/点击弹跳（transform scale + cubic-bezier），过关时飘星星/彩带（纯CSS/JS实现，不用库）
- 进度条做成可爱的「糖果条」
- 整体轻松、治愈，不要商务冷淡风

## 结构
### 1. 开场弹窗（每次打开页面都先弹出）
- 标题：今天想练点什么？🌤️
- 选主题（多选，卡片式，带emoji）
- 选今日目标：3关 / 5关 / 10关（按钮选择）
- 「开始今天的学习 🚀」按钮 → 关闭弹窗进主界面
- 保存到 localStorage（记住上次选择，下次预填）

### 2. 主界面
- 顶部：今日任务进度（如 2/5 关）+ 糖果进度条 + 连续学习天数🔥
- 主题分区 → 每主题一条闯关小径（圆形关卡气泡 + 虚线连接）
- 点关卡气泡进入学习页
- 右上角小按钮：重新设定今日任务（重新打开开场弹窗）

### 3. 关卡学习页（每关 = 一个单词，分段展示）
分 3 步渐进展示（可用「下一步」按钮逐步展开，也可直接全展示 — 请实现为逐步展开更有闯关感）：
- **Step 1 学词**：大号英文单词 + 🔊 发音按钮（用 Web Speech API speechSynthesis 读英文，不联网）+ 音标
- **Step 2 英英释义**：用**纯英文**解释这个词（词典风格，简洁地道，1-2句）+ 例句
- **Step 3 用法与词性**：词性标注（n. / v. / adj. / adv. 等）+ 2-3 个常用搭配（搭配英文 + 中文） + 2 个例句（英文 + 中文对照）
- 底部按钮：「✅ 学会啦，过关！」→ 播放星星动效，标记过关、解锁下一关、返回地图；「← 返回」

## 内容（自己写，要地道、有梯度）
6 个主题，每主题 6 个词 = 36 关：
1. 🌱 Daily Life（日常）— 如 cozy, run errands, tidy, commute, chore, leisure
2. 🍰 Food & Eating（饮食）— 如 crave, savory, leftovers, appetizing, portion, dine out
3. ✈️ Travel（旅行）— 如 itinerary, wander, breathtaking, layover, off the beaten track, getaway
4. 💼 Work & Study（工作学习）— 如 deadline, productive, collaborate, workload, procrastinate, skill set
5. 💻 Technology（科技）— 如 gadget, seamless, glitch, user-friendly, upgrade, cutting-edge
6. 🗣️ Opinions & Society（观点社会）— 如 controversial, advocate, mainstream, biased, sustainable, perspective
（可自行微调选词，但要保证每个词都有独立的英英释义+词性+搭配+例句）

每关数据字段：
id, topic, word, phonetic, meaning_en（英英释义）, meaning_example_en（释义配的例句）,
pos（词性）, collocations:[{en,zh}], examples:[{en,zh}]
优先收录「短语/搭配」类（如 run errands, dine out）也可以单列为词条。

## 技术
- 纯原生 HTML/CSS/JS，无外部请求
- 数据用 JS 常量数组，与渲染分离，文件顶部写清「如何加新词」注释
- localStorage key: vocab_quest_v1（结构：{passedLevelIds:[], streak, lastStudyDate, todayGoal, selectedTopics}）
- 响应式：手机单列、大按钮；桌面居中窄栏（max-width ~720px）
- 一次性完整实现，不要 TODO 占位

## 约束
- 不要修改/删除工作区其它文件
- 完整可运行，写完自查（node --check 校验提取的JS）
