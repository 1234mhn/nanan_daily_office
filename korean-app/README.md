# 韩语单词大冒险 🎮

可爱软萌的韩语单词学习应用 - 阶段一：首页

## 📦 项目信息

- **技术栈**: Next.js 15 (App Router) + TypeScript + TailwindCSS
- **UI 组件**: shadcn/ui
- **部署方式**: 静态导出 (Static Export)
- **部署路径**: `/korean-app`

## 🎯 当前功能

✅ 首页（闯关选择页）
- 6 个关卡卡片展示
- 三种状态：已通关、当前可解锁、未解锁
- 星星评价系统（3 星制）
- 进度条显示
- 卡通头像 + 学习统计

✅ 路由占位页
- `/dictionary` - 单词词典（占位）
- `/chat` - AI 对话答疑（占位）
- `/level/[id]` - 闯关答题页（占位）

## 🎨 设计特色

- 🍭 可爱卡通软萌风格
- 🌈 马卡龙配色（低饱和度）
- 📐 超大圆角（rounded-3xl / 2rem）
- ✨ 柔和渐变背景
- 💫 Hover 动画效果
- 📱 移动端友好

## 📁 项目结构

```
korean-app/
├── app/                        # Next.js App Router
│   ├── layout.tsx             # 根布局
│   ├── page.tsx               # 首页（闯关选择）
│   ├── globals.css            # 全局样式
│   ├── chat/                  # AI 对话页（占位）
│   ├── dictionary/            # 单词词典页（占位）
│   └── level/[id]/            # 闯关答题页（占位）
├── components/                 # React 组件
│   ├── ui/                    # shadcn/ui 基础组件
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── progress.tsx
│   ├── user-header.tsx        # 顶部用户信息栏
│   ├── level-card.tsx         # 关卡卡片
│   └── navigation-buttons.tsx # 底部导航按钮
├── lib/                       # 工具库
│   ├── storage.ts            # localStorage 封装
│   ├── levels.ts             # 关卡配置数据
│   └── utils.ts              # 工具函数
├── next.config.ts            # Next.js 配置
├── tailwind.config.ts        # Tailwind 配置
└── package.json
```

## 🚀 开发命令

```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 构建静态站点
npm run build

# 查看构建结果
ls -la out/
```

## 📊 构建结果

✅ **构建成功** - 2026/09/17

```
Route (app)                                 Size  First Load JS
┌ ○ /                                    5.12 kB         120 kB
├ ○ /chat                                1.73 kB         116 kB
├ ○ /dictionary                          1.73 kB         116 kB
└ ● /level/[id]                            161 B         106 kB
    ├ /level/1
    ├ /level/2
    ├ /level/3
    ├ /level/4
    ├ /level/5
    └ /level/6
```

- 所有页面已成功静态导出至 `out/` 目录
- 6 个关卡页面全部预渲染完成
- 静态资源已优化，包含 CSS/JS chunks

## 💾 数据存储

- 使用 **localStorage** 存储用户进度
- 统一封装在 `lib/storage.ts`
- 接口设计便于将来替换为 API 调用

### 数据结构

```typescript
interface UserProgress {
  totalWords: number        // 累计学习单词数
  totalStars: number       // 总获得星星数
  currentLevel: number     // 当前解锁关卡
  levelProgress: {
    [levelId]: {
      completed: boolean   // 是否通关
      stars: number       // 获得星星（0-3）
      progress: number    // 进度百分比（0-100）
    }
  }
}
```

### 默认数据

- 第 1 关：已完成（3 星，100%）
- 第 2 关：当前解锁（0 星，0%）
- 第 3-6 关：未解锁

## 🎮 关卡配置

6 个示例关卡（`lib/levels.ts`）：

1. 🍎 基础名词 - 20 个单词
2. 🏃 常用动词 - 25 个单词
3. 🎨 形容词宝库 - 22 个单词
4. 💬 日常对话 - 18 个单词
5. 🍜 美食天地 - 30 个单词
6. ✈️ 旅行韩国 - 28 个单词

## 🔮 后续扩展

- [ ] 闯关答题页实现
- [ ] 单词词典页实现
- [ ] AI 对话答疑实现
- [ ] 音频播放功能
- [ ] 成就系统
- [ ] 每日打卡

## 📝 注意事项

- ⚠️ 不要修改 `/www/korean_course/` 目录
- ⚠️ 不要修改 `/www/korean_vocab/` 目录
- 🔧 basePath 已配置为 `/korean-app`
- 🌐 部署目标：https://nannan2026.cn/korean-app/

---

**开发日期**: 2026-09-17  
**状态**: ✅ 阶段一完成
