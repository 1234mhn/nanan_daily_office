import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { ArrowLeft } from 'lucide-react'
import { LEVELS } from '@/lib/levels'

// 静态导出时生成所有关卡页面
export function generateStaticParams() {
  return LEVELS.map((level) => ({
    id: level.id.toString(),
  }))
}

export default async function LevelPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 via-orange-50 to-red-50 py-8 px-4">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* 返回按钮 */}
        <Link href="/">
          <Button
            variant="outline"
            size="lg"
            className="gap-2 bg-white/80 backdrop-blur-sm hover:bg-white"
          >
            <ArrowLeft className="w-4 h-4" />
            返回首页
          </Button>
        </Link>

        {/* 占位内容 */}
        <Card className="p-12 text-center space-y-6 bg-white/60 backdrop-blur-sm">
          <div className="flex justify-center">
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-yellow-200 to-orange-200 flex items-center justify-center shadow-lg text-4xl">
              🎮
            </div>
          </div>

          <div className="space-y-3">
            <h1 className="text-3xl md:text-4xl font-bold text-foreground">
              第 {id} 关
            </h1>
            <p className="text-lg text-muted-foreground">
              闯关答题页面
            </p>
            <p className="text-sm text-muted-foreground">
              功能开发中，敬请期待... 🎯
            </p>
          </div>
        </Card>
      </div>
    </div>
  )
}
