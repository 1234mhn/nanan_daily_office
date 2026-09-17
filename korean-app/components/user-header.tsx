'use client'

interface UserHeaderProps {
  totalWords: number
  totalStars: number
}

export function UserHeader({ totalWords, totalStars }: UserHeaderProps) {
  return (
    <div className="flex items-center justify-center gap-6 p-6 bg-white/60 backdrop-blur-sm rounded-[2rem] shadow-lg border border-white/40">
      {/* 卡通头像 */}
      <div className="w-16 h-16 rounded-full bg-gradient-to-br from-pink-300 to-purple-300 flex items-center justify-center text-3xl shadow-md">
        🐰
      </div>

      {/* 统计信息 */}
      <div className="flex gap-8">
        <div className="text-center">
          <div className="text-2xl font-bold text-foreground">{totalWords}</div>
          <div className="text-sm text-muted-foreground">学习单词</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-foreground flex items-center justify-center gap-1">
            {totalStars}
            <span className="text-yellow-400">⭐</span>
          </div>
          <div className="text-sm text-muted-foreground">获得星星</div>
        </div>
      </div>
    </div>
  )
}
