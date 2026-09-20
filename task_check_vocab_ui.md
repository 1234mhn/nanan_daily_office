# 任务：查看韩语单词岛屿主界面截图，理解用户意图

## 背景
用户（产品主人）发来一张手机截图，我们（AI）看不了图（视觉模型失效），需要你（Claude Code）直接读图。

## 截图路径
/root/.openclaw/workspace/media/tmp_review/ 下有 3 张切图：
- shot_top.jpg（上半）
- shot_mid.jpg（中段）
- shot_bot.jpg（下半）

原始完整图：/root/.openclaw/workspace/media/inbound/openclaw-staged-534f39b1-7b70-48d8-a7a9-ee7bd9006cb9/34bb6ce8-7d1b-4a7a-a3bd-16bf1390ac8d.jpg

## 你要做的事
1. 用你的读图能力，把截图内容**如实描述**出来：页面标题、所有可见文字、按钮、卡片、地图元素、布局结构、配色。
2. 判断：这是不是韩语单词岛屿页面（/www/korean_vocab/index.html）的界面？还是别的页面？
3. 对照实际代码：读 /www/korean_vocab/index.html，找出截图对应的是哪个区块（homePage / questMapPage / learnPage）。
4. 指出截图与实际代码**有没有不一致的地方**（比如截图是旧版本界面、或某个元素代码里没有）。

## 输出要求
- 纯文字报告，直接说结论
- 不要修改任何文件
- 不要运行服务器操作

## 重要
只读，不改。看完写一份简短报告即可。
