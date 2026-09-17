'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { ArrowLeft, BookOpen } from 'lucide-react'

export default function DictionaryPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-teal-50 py-8 px-4">
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
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-200 to-cyan-200 flex items-center justify-center shadow-lg">
              <BookOpen className="w-12 h-12 text-blue-600" />
            </div>
          </div>

          <div className="space-y-3">
            <h1 className="text-3xl md:text-4xl font-bold text-foreground">
              单词词典
            </h1>
            <p className="text-lg text-muted-foreground">
              这里将展示所有学习过的单词
            </p>
            <p className="text-sm text-muted-foreground">
              功能开发中，敬请期待... 🎨
            </p>
          </div>
        </Card>
      </div>
    </div>
  )
}
