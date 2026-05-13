import { useCallback, useState } from 'react'
import type { Message } from '../types'
import { streamChat } from '../utils/api'

export function useChat(sessionId: string) {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const sendMessage = useCallback(
    async (userInput: string) => {
      if (!userInput.trim() || isLoading) return

      setError(null)

      const userMsg: Message = {
        id: crypto.randomUUID(),
        role: 'user',
        content: userInput.trim(),
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, userMsg])
      setIsLoading(true)

      const assistantId = crypto.randomUUID()
      const assistantMsg: Message = {
        id: assistantId,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        isStreaming: true,
      }
      setMessages((prev) => [...prev, assistantMsg])

      // Build history for context (last 10 exchanges)
      const history = messages.slice(-10).map((m) => ({
        role: m.role,
        content: m.content,
      }))

      await streamChat(
        { session_id: sessionId, message: userInput.trim(), history },
        (token) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, content: m.content + token } : m,
            ),
          )
        },
        () => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, isStreaming: false } : m,
            ),
          )
          setIsLoading(false)
        },
        (err) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? { ...m, content: `⚠️ ${err}`, isStreaming: false }
                : m,
            ),
          )
          setError(err)
          setIsLoading(false)
        },
      )
    },
    [messages, sessionId, isLoading],
  )

  const clearMessages = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  return { messages, isLoading, error, sendMessage, clearMessages }
}
