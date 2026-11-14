/**
 * 关卡配置数据
 */

export interface Level {
  id: number
  name: string
  description: string
  emoji: string // 关卡装饰 emoji
  wordCount: number // 本关单词数
}

export const LEVELS: Level[] = [
  {
    id: 1,
    name: '基础名词',
    description: '学习日常生活中的常见名词',
    emoji: '🍎',
    wordCount: 20,
  },
  {
    id: 2,
    name: '常用动词',
    description: '掌握韩语中最常用的动作词汇',
    emoji: '🏃',
    wordCount: 25,
  },
  {
    id: 3,
    name: '形容词宝库',
    description: '描述事物特征的必备词汇',
    emoji: '🎨',
    wordCount: 22,
  },
  {
    id: 4,
    name: '日常对话',
    description: '问候、感谢等交流必备表达',
    emoji: '💬',
    wordCount: 18,
  },
  {
    id: 5,
    name: '美食天地',
    description: '韩国料理相关词汇大集合',
    emoji: '🍜',
    wordCount: 30,
  },
  {
    id: 6,
    name: '旅行韩国',
    description: '旅游场景常用词汇',
    emoji: '✈️',
    wordCount: 28,
  },
]

/**
 * 根据 ID 获取关卡信息
 */
export function getLevelById(id: number): Level | undefined {
  return LEVELS.find((level) => level.id === id)
}
