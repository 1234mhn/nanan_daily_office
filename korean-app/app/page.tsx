'use client'

import { useEffect, useState } from 'react'
import { LEVELS } from '@/lib/levels'
import { getUserProgress, getDefaultProgress, type UserProgress } from '@/lib/storage'
import { UserHeader } from '@/components/user-header'
import { LevelCard } from '@/components/level-card'
import { NavigationButtons } from '@/components/navigation-buttons'

export default function HomePage() {
  // 使用默认进度初始化，确保首屏有内容（SSR 安全）
  const [userProgress, setUserProgress] = useState<UserProgress>(getDefaultProgress())

  useEffect(() => {
    // 客户端挂载后，加载真实用户进度
    setUserProgress(getUserProgress())
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-blue-50 to-purple-50 py-8 px-4">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* 顶部用户信息 */}
        <UserHeader
          totalWords={userProgress.totalWords}
          totalStars={userProgress.totalStars}
        />

        {/* 页面标题 */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl md:text-5xl font-bold text-foreground">
            韩语单词大冒险
          </h1>
          <p className="text-muted-foreground text-lg">
            选择关卡，开始你的学习之旅 🚀
          </p>
        </div>

        {/* 关卡网格 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {LEVELS.map((level) => {
            const levelProgress = userProgress.levelProgress[level.id] || {
              completed: false,
              stars: 0,
              progress: 0,
            }

            // 确定关卡状态
            const isCompleted = levelProgress.completed
            const isUnlocked = level.id <= userProgress.currentLevel
            const isCurrent = level.id === userProgress.currentLevel

            return (
              <LevelCard
                key={level.id}
                level={level}
                progress={levelProgress}
                isCompleted={isCompleted}
                isUnlocked={isUnlocked}
                isCurrent={isCurrent}
              />
            )
          })}
        </div>

        {/* 底部导航按钮 */}
        <NavigationButtons />
      </div>
    </div>
  )
}
