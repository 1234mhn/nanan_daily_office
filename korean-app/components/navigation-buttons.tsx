'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { BookOpen, MessageCircle } from 'lucide-react'

export function NavigationButtons() {
  return (
    <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-8">
      <Link href="/dictionary" className="w-full sm:w-auto">
        <Button
          variant="outline"
          size="lg"
          className="w-full sm:w-64 h-14 bg-white/80 backdrop-blur-sm hover:bg-white hover:shadow-lg border-2 border-blue-200 text-blue-600 font-bold gap-2"
        >
          <BookOpen className="w-5 h-5" />
          单词词典
        </Button>
      </Link>

      <Link href="/chat" className="w-full sm:w-auto">
        <Button
          variant="outline"
          size="lg"
          className="w-full sm:w-64 h-14 bg-white/80 backdrop-blur-sm hover:bg-white hover:shadow-lg border-2 border-purple-200 text-purple-600 font-bold gap-2"
        >
          <MessageCircle className="w-5 h-5" />
          AI 对话答疑
        </Button>
      </Link>
    </div>
  )
}
