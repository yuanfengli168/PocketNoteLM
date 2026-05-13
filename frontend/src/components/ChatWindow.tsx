import { useEffect, useRef } from 'react'
import type { Message } from '../types'
import { MessageBubble } from './Message'
import styles from './ChatWindow.module.css'

interface Props {
  messages: Message[]
  isLoading: boolean
}

export function ChatWindow({ messages, isLoading }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  if (messages.length === 0) {
    return (
      <div className={styles.empty}>
        <div className={styles.emptyInner}>
          <p className={styles.emptyIcon}>🧩</p>
          <p className={styles.emptyTitle}>PocketNoteLM</p>
          <p className={styles.emptySubtitle}>
            Ask me anything about your documents — drop in PDFs or notes and start exploring.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.window}>
      <div className={styles.messages}>
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {isLoading && messages[messages.length - 1]?.role !== 'assistant' && (
          <div className={styles.typing}>
            <span /><span /><span />
          </div>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
