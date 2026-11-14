import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "韩语单词大冒险",
  description: "可爱的韩语单词学习应用",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="zh-CN">
      <body className="antialiased min-h-screen">
        {children}
      </body>
    </html>
  )
}
