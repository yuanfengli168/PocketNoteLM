import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { Message } from '../types'
import styles from './Message.module.css'

interface Props {
  message: Message
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === 'user'

  return (
    <div className={`${styles.row} ${isUser ? styles.userRow : styles.assistantRow}`}>
      <div className={`${styles.avatar} ${isUser ? styles.userAvatar : styles.botAvatar}`}>
        {isUser ? 'You' : 'AI'}
      </div>
      <div className={`${styles.bubble} ${isUser ? styles.userBubble : styles.botBubble}`}>
        {isUser ? (
          <p className={styles.plainText}>{message.content}</p>
        ) : (
          <div className={styles.markdown}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content || (message.isStreaming ? '▋' : '')}
            </ReactMarkdown>
          </div>
        )}
        {message.isStreaming && !isUser && (
          <span className={styles.cursor}>▋</span>
        )}
      </div>
    </div>
  )
}
