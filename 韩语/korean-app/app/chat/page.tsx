'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { ArrowLeft, MessageCircle } from 'lucide-react'

export default function ChatPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-rose-50 py-8 px-4">
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
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-purple-200 to-pink-200 flex items-center justify-center shadow-lg">
              <MessageCircle className="w-12 h-12 text-purple-600" />
            </div>
          </div>

          <div className="space-y-3">
            <h1 className="text-3xl md:text-4xl font-bold text-foreground">
              AI 对话答疑
            </h1>
            <p className="text-lg text-muted-foreground">
              AI 助手将帮助你解答韩语学习中的问题
            </p>
            <p className="text-sm text-muted-foreground">
              功能开发中，敬请期待... 🤖
            </p>
          </div>
        </Card>
      </div>
    </div>
  )
}
