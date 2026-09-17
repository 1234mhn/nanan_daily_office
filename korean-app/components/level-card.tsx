'use client'

import Link from 'next/link'
import { Card } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Button } from '@/components/ui/button'
import { Lock } from 'lucide-react'
import type { Level } from '@/lib/levels'
import type { LevelProgress } from '@/lib/storage'

interface LevelCardProps {
  level: Level
  progress: LevelProgress
  isCompleted: boolean
  isUnlocked: boolean
  isCurrent: boolean
}

export function LevelCard({
  level,
  progress,
  isCompleted,
  isUnlocked,
  isCurrent,
}: LevelCardProps) {
  // 星星渲染
  const renderStars = () => {
    return (
      <div className="flex gap-1 justify-center">
        {[1, 2, 3].map((star) => (
          <span
            key={star}
            className={`text-2xl transition-all ${
              star <= progress.stars
                ? 'text-yellow-400 scale-110'
                : 'text-gray-300'
            }`}
          >
            ⭐
          </span>
        ))}
      </div>
    )
  }

  // 未解锁状态
  if (!isUnlocked) {
    return (
      <Card className="relative overflow-hidden bg-gray-100 border-gray-200 opacity-60 cursor-not-allowed">
        <div className="p-6 space-y-4">
          {/* 锁图标 */}
          <div className="flex justify-center">
            <div className="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center">
              <Lock className="w-8 h-8 text-gray-400" />
            </div>
          </div>

          {/* 关卡信息 */}
          <div className="text-center space-y-2">
            <div className="text-sm text-gray-400">第 {level.id} 关</div>
            <h3 className="text-xl font-bold text-gray-500">{level.name}</h3>
            <p className="text-sm text-gray-400 min-h-[40px]">
              {level.description}
            </p>
          </div>

          {/* 星星占位 */}
          <div className="flex gap-1 justify-center">
            {[1, 2, 3].map((star) => (
              <span key={star} className="text-2xl text-gray-300">
                ⭐
              </span>
            ))}
          </div>
        </div>
      </Card>
    )
  }

  // 已完成状态
  if (isCompleted) {
    return (
      <Link href={`/level/${level.id}`} className="block">
        <Card className="relative overflow-hidden bg-gradient-to-br from-green-100 to-teal-100 border-green-200 hover:shadow-xl hover:-translate-y-2 transition-all duration-300 cursor-pointer">
          {/* 完成标记 */}
          <div className="absolute top-4 right-4 text-3xl">✅</div>

          <div className="p-6 space-y-4">
            {/* Emoji 图标 */}
            <div className="flex justify-center">
              <div className="w-16 h-16 rounded-full bg-white/80 flex items-center justify-center text-4xl shadow-md">
                {level.emoji}
              </div>
            </div>

            {/* 关卡信息 */}
            <div className="text-center space-y-2">
              <div className="text-sm text-green-600 font-medium">
                第 {level.id} 关
              </div>
              <h3 className="text-xl font-bold text-foreground">
                {level.name}
              </h3>
              <p className="text-sm text-muted-foreground min-h-[40px]">
                {level.description}
              </p>
            </div>

            {/* 星星评价 */}
            {renderStars()}

            {/* 进度条 */}
            <Progress value={progress.progress} className="h-2" />
          </div>
        </Card>
      </Link>
    )
  }

  // 当前可解锁状态
  return (
    <Link href={`/level/${level.id}`} className="block">
      <Card className="relative overflow-hidden bg-gradient-to-br from-pink-100 via-purple-100 to-blue-100 border-pink-200 hover:shadow-2xl hover:-translate-y-2 hover:scale-105 transition-all duration-300 cursor-pointer animate-pulse">
        {/* 闪烁提示 */}
        <div className="absolute top-2 right-2 text-2xl animate-bounce">✨</div>

        <div className="p-6 space-y-4">
          {/* Emoji 图标 */}
          <div className="flex justify-center">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-yellow-200 to-orange-200 flex items-center justify-center text-4xl shadow-lg ring-4 ring-yellow-300/50">
              {level.emoji}
            </div>
          </div>

          {/* 关卡信息 */}
          <div className="text-center space-y-2">
            <div className="text-sm text-pink-600 font-bold">
              第 {level.id} 关
            </div>
            <h3 className="text-xl font-bold text-foreground">{level.name}</h3>
            <p className="text-sm text-muted-foreground min-h-[40px]">
              {level.description}
            </p>
          </div>

          {/* 星星评价 */}
          {renderStars()}

          {/* 开始按钮 */}
          <Button
            className="w-full bg-gradient-to-r from-pink-400 to-purple-400 hover:from-pink-500 hover:to-purple-500 text-white font-bold text-lg h-12 shadow-lg"
            size="lg"
          >
            开始闯关 🎯
          </Button>

          {/* 进度条 */}
          {progress.progress > 0 && (
            <Progress value={progress.progress} className="h-2" />
          )}
        </div>
      </Card>
    </Link>
  )
}
