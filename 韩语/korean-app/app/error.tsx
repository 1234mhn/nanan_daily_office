'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // 记录错误到控制台
    console.error('应用错误:', error)
  }, [error])

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-orange-50 to-yellow-50 flex items-center justify-center p-4">
      <Card className="p-12 max-w-lg text-center space-y-6 bg-white/80 backdrop-blur-sm">
        <div className="flex justify-center">
          <div className="w-24 h-24 rounded-full bg-gradient-to-br from-red-200 to-orange-200 flex items-center justify-center shadow-lg text-4xl">
            😅
          </div>
        </div>

        <div className="space-y-3">
          <h1 className="text-3xl font-bold text-foreground">出错了</h1>
          <p className="text-muted-foreground">
            应用遇到了一些问题，请尝试重新加载
          </p>
          {process.env.NODE_ENV === 'development' && (
            <details className="mt-4 text-left text-sm text-red-600 bg-red-50 p-4 rounded-lg">
              <summary className="cursor-pointer font-medium">
                错误详情（开发模式）
              </summary>
              <pre className="mt-2 whitespace-pre-wrap break-words">
                {error.message}
              </pre>
            </details>
          )}
        </div>

        <div className="flex gap-4 justify-center">
          <Button
            onClick={() => reset()}
            className="bg-gradient-to-r from-blue-400 to-purple-400 hover:from-blue-500 hover:to-purple-500"
          >
            重试
          </Button>
          <Button
            variant="outline"
            onClick={() => (window.location.href = '/')}
          >
            返回首页
          </Button>
        </div>
      </Card>
    </div>
  )
}
