export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  isStreaming?: boolean
}

export interface ChatRequest {
  session_id: string
  message: string
  history: Array<{ role: string; content: string }>
}
